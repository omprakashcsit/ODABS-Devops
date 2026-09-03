import re
from datetime import date, datetime

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.cache import never_cache

from appointment.models import Appointment
from appointment.views import generate_slots
from doctors.models import Doctor
from doctors.ranking import calculate_score_with_breakdown
from notifications.models import Notification
from notifications.services import create_notification, send_notification_email

from .models import Patients

from security.config import ENCRYPTION_KEY

from .security import (
    encrypt_patient_data,
    decrypt_patient_data,
    create_lookup,
)


# User registration
def register(request):

    if request.method == "POST":

        name = request.POST["name"].strip()
        email = request.POST["email"].strip()
        phone = request.POST["phone"].strip()
        address = request.POST["address"].strip()
        dob = request.POST["dob"]
        gender = request.POST["gender"]

        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        errors = {}

        try:
            dob_date = datetime.strptime(
                dob,
                "%Y-%m-%d"
            ).date()
        except (ValueError, TypeError):
            errors["dob"] = "Enter a valid date of birth."
            dob_date = None

        today = date.today()

        if dob_date:

            age = today.year - dob_date.year - (
                (today.month, today.day) <
                (dob_date.month, dob_date.day)
            )

            # Date of birth validation
            if dob_date > today:
                errors["dob"] = (
                    "Date of birth cannot be in the future."
                )

            elif age < 0 or age > 122:
                errors["dob"] = (
                    "Age must be between 0 and 122 years."
                )

        # Validate phone number
        if not re.fullmatch(r"9[678]\d{8}", phone):
            errors["phone"] = (
                "Enter a valid Nepali phone number."
            )

        # Check duplicate phone
        # Check duplicate phone using secure lookup
        phone_lookup = create_lookup(
            phone,
            ENCRYPTION_KEY
        )

        if Patients.objects.filter(
            phone_lookup=phone_lookup
        ).exists():
            errors["phone"] = (
                "Phone number is already registered."
            )

        # Check duplicate email
        # Check duplicate email using secure lookup
        email_lookup = create_lookup(
            email,
            ENCRYPTION_KEY
        )

        if Patients.objects.filter(
            email_lookup=email_lookup
        ).exists():
            errors["email"] = (
                "Email is already registered."
            )

        # Check password confirmation
        if password != confirm_password:
            errors["confirm_password"] = (
                "Passwords do not match."
            )

        # Password length
        if len(password) < 8:
            errors["password"] = (
                "Password must be at least 8 characters."
            )

        # Uppercase letter
        if not re.search(r"[A-Z]", password):
            errors["password"] = (
                "Password must contain an uppercase letter."
            )

        # Lowercase letter
        if not re.search(r"[a-z]", password):
            errors["password"] = (
                "Password must contain a lowercase letter."
            )

        # Number
        if not re.search(r"\d", password):
            errors["password"] = (
                "Password must contain a number."
            )

        # Special character
        if not re.search(
            r"[!@#$%^&*(),.?\":{}|<>]",
            password
        ):
            errors["password"] = (
                "Password must contain a special character."
            )

        if errors:

            return render(
                request,
                "HomePage/landing.html",
                {
                    "register_errors": errors,
                    "form_data": request.POST,
                    "show_register_modal": True,
                },
            )

        # Generate hidden username
        username = f"pt{phone}"

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        patient = Patients.objects.create(
            user=user,
            name=name,
            email=email,
            phone=phone,
            address=address,
            dob=dob_date,
            gender=gender
        )

        encrypt_patient_data(
            patient,
            ENCRYPTION_KEY
        )

        patient.save(
            update_fields=[
                "encrypted_name",
                "encrypted_email",
                "encrypted_address",
                "encrypted_phone",
                "encrypted_dob",
                "encrypted_gender",
                "phone_lookup",
                "email_lookup",
            ]
        )

        login(request, user)

        # Send welcome email
        send_notification_email(
            patient=patient,
            subject="Welcome to ODAS",
            message=(
                f"Hello {name},\n\n"
                "Welcome to the Online Doctor Appointment System.\n\n"
                "Your account has been created successfully."
            )
        )

        # Create welcome notification
        create_notification(
            patient=user,
            title="Welcome to ODAS",
            message=(
                "Your account has been created successfully. "
                "You can now search for doctors and book appointments."
            ),
            notification_type="system",
            reminder_type="general",
        )

        messages.success(
            request,
            "Registration completed successfully."
        )

        return redirect("patient_dashboard")

    return redirect("home")


# Login with phone number or username
@never_cache
def user_login(request):

    # Prevent logged-in users from accessing login page
    if request.user.is_authenticated:

        # Admin
        if (
            request.user.is_superuser
            or request.user.is_staff
        ):
            return redirect("admin_dashboard")

        # Doctor
        elif Doctor.objects.filter(
            user=request.user
        ).exists():
            return redirect("doctor_dashboard")

        # Patient
        return redirect("patient_dashboard")

    if request.method == "POST":

        login_id = request.POST["login_id"].strip()
        password = request.POST["password"]

        # Patient login using phone number
        if re.fullmatch(
            r"9[678]\d{8}",
            login_id
        ):

            phone_lookup = create_lookup(
                login_id,
                ENCRYPTION_KEY
            )

            patient = Patients.objects.filter(
                phone_lookup=phone_lookup
            ).first()

            if (
                patient is None
                or patient.user is None
            ):

                return render(
                    request,
                    "HomePage/landing.html",
                    {
                        "login_errors": {
                            "login_id": (
                                "Phone number is not registered."
                            )
                        },
                        "login_data": request.POST,
                        "show_login_modal": True,
                    },
                )

            user = authenticate(
                request,
                username=patient.user.username,
                password=password
            )

        # Doctor/Admin login using username
        else:

            user = authenticate(
                request,
                username=login_id,
                password=password
            )

        if user is None:

            return render(
                request,
                "HomePage/landing.html",
                {
                    "login_errors": {
                        "general": (
                            "Invalid username/phone number "
                            "or password."
                        )
                    },
                    "login_data": request.POST,
                    "show_login_modal": True,
                }
            )

        login(request, user)

        # Redirect according to role
        if user.is_superuser or user.is_staff:
            return redirect("admin_dashboard")

        elif Doctor.objects.filter(
            user=user
        ).exists():
            return redirect("doctor_dashboard")

        # Patient
        next_url = request.POST.get("next")

        if next_url:
            return redirect(next_url)

        return redirect("patient_dashboard")

    return redirect("home")


# Logout
def user_logout(request):

    logout(request)

    return redirect("home")


# Patient dashboard
@login_required
def patient_dashboard(request):

    patient = Patients.objects.filter(
        user=request.user
    ).first()

    if patient:
        decrypt_patient_data(
            patient,
            ENCRYPTION_KEY
        )

    if not patient:

        messages.error(
            request,
            "Patient profile not found."
        )

        return redirect("logout")

    appointments = Appointment.objects.filter(
        patient=request.user
    ).order_by(
        "appointment_date",
        "appointment_time"
    )

    today = timezone.localdate()

    upcoming = appointments.filter(
        appointment_date__gte=today,
        status="upcoming"
    ).order_by(
        "appointment_date",
        "appointment_time"
    )

    past = appointments.filter(
        appointment_date__lt=today
    )

    # Appointment statistics
    completed = appointments.filter(
        status="completed"
    ).count()

    upcoming_count = appointments.filter(
        status="upcoming"
    ).count()

    cancelled = appointments.filter(
        status="cancelled"
    ).count()

    missed = appointments.filter(
        status="missed"
    ).count()

    # Recommended doctors
    recommended = []

    doctors = Doctor.objects.filter(
        a_status=True
    )

    for doctor in doctors:

        score, breakdown = calculate_score_with_breakdown(
            doctor
        )

        recommended.append({
            "doctor": doctor,
            "score": score,
            "breakdown": breakdown
        })

    recommended.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    recommended = recommended[:3]

    # Get latest three notifications
    notifications = Notification.objects.filter(
        patient=request.user
    ).order_by(
        "-created_at"
    )[:3]

    # Count unread notifications
    unread_notifications = Notification.objects.filter(
        patient=request.user,
        is_read=False
    ).count()

    for appointment in upcoming:
        print(
            "APPOINTMENT:",
            appointment.appointment_id,
            appointment.appointment_date,
            appointment.appointment_time,
            "PROBABILITY:",
            appointment.no_show_probability,
            "PREDICTION:",
            appointment.no_show_prediction,
            "CONFIRMED:",
            appointment.attendance_confirmed
        )

    # Do not automatically mark notifications as read here.
    # Notifications remain unread until the patient explicitly opens them.

    return render(
        request,
        "patients/patient_dashboard.html",
        {
            "patient": patient,
            "upcoming": upcoming,
            "past": past,
            "upcoming_count": upcoming_count,
            "completed": completed,
            "cancelled": cancelled,
            "missed": missed,
            "recommended": recommended,
            "notifications": notifications,
            "unread_notifications": unread_notifications,
        }
    )


# Appointment detail
@login_required
def appointment_detail(
    request,
    appointment_id
):

    appointment = get_object_or_404(
        Appointment,
        appointment_id=appointment_id,
        patient=request.user
    )

    return render(
        request,
        "patients/appointment_detail.html",
        {
            "appointment": appointment
        }
    )


# Cancel appointment
@login_required
def cancel_appointment(
    request,
    appointment_id
):

    appointment = get_object_or_404(
        Appointment,
        appointment_id=appointment_id,
        patient=request.user
    )

    if request.method == "POST":

        if appointment.status == "upcoming":

            appointment.status = "cancelled"

            appointment.save(
                update_fields=["status"]
            )

            create_notification(
                patient=request.user,
                appointment=appointment,
                title="Appointment Cancelled",
                message=(
                    f"Your appointment with "
                    f"Dr. {appointment.doctor.name} "
                    f"has been cancelled."
                ),
                notification_type="appointment",
                reminder_type="general",
            )

            messages.success(
                request,
                "Appointment cancelled successfully."
            )

        else:

            messages.warning(
                request,
                "This appointment cannot be cancelled."
            )

    return redirect("patient_dashboard")


# Success page
def success(request):

    return render(
        request,
        "patients/success.html"
    )


# Appointment list by status
@login_required
def appointment_list(
    request,
    status
):

    appointments = Appointment.objects.filter(
        patient=request.user,
        status=status
    ).select_related(
        "doctor",
        "doctor__hospital"
    ).order_by(
        "appointment_date",
        "appointment_time"
    )

    # Automatically update expired upcoming appointments
    if status == "upcoming":

        now = timezone.localtime()

        valid_appointments = []

        for appointment in appointments:

            appointment_datetime = get_appt_datetime(
                appointment
            )

            if appointment_datetime < now:

                appointment.status = "missed"

                appointment.save(
                    update_fields=["status"]
                )

                create_notification(
                    patient=request.user,
                    appointment=appointment,
                    title="Appointment Missed",
                    message=(
                        f"Your appointment with "
                        f"Dr. {appointment.doctor.name} "
                        f"was marked as missed."
                    ),
                    notification_type="appointment",
                    reminder_type="general",
                )

            else:

                valid_appointments.append(
                    appointment
                )

        appointments = valid_appointments

    return render(
        request,
        "patients/appointment_list.html",
        {
            "appointments": appointments,
            "status": status.title()
        }
    )


# Reschedule appointment
@login_required
def reschedule_appointment(
    request,
    appointment_id
):

    appointment = get_object_or_404(
        Appointment,
        appointment_id=appointment_id,
        patient=request.user
    )

    slots = []

    selected_date = request.GET.get("date")

    if not selected_date:

        selected_date = (
            appointment.appointment_date
            .strftime("%Y-%m-%d")
        )

    if selected_date:

        slots = generate_slots(
            appointment.doctor,
            selected_date,
            exclude_appointment=appointment
        )

        if not slots:

            messages.error(
                request,
                "Doctor is not available on the selected date. "
                "Please choose another date."
            )

    if request.method == "POST":

        appointment_date = request.POST.get(
            "appointment_date"
        )

        appointment_time = request.POST.get(
            "appointment_time"
        )

        try:

            appointment_date_obj = datetime.strptime(
                appointment_date,
                "%Y-%m-%d"
            ).date()

        except (ValueError, TypeError):

            messages.error(
                request,
                "Please select a valid appointment date."
            )

            return redirect(
                "reschedule_appointment",
                appointment_id=appointment.appointment_id
            )

        # Prevent rescheduling to a past date
        if appointment_date_obj < timezone.localdate():

            messages.error(
                request,
                "You cannot reschedule to a past date."
            )

            return redirect(
                "reschedule_appointment",
                appointment_id=appointment.appointment_id
            )

        slots = generate_slots(
            appointment.doctor,
            appointment_date,
            exclude_appointment=appointment
        )

        if (
            not appointment_time
            or appointment_time not in slots
        ):

            messages.error(
                request,
                "Selected time is not available."
            )

            return redirect(
                "reschedule_appointment",
                appointment_id=appointment.appointment_id
            )

        appointment.appointment_date = (
            appointment_date_obj
        )

        appointment.appointment_time = (
            appointment_time
        )

        appointment.status = "upcoming"

        appointment.save()

        # Notify patient
        create_notification(
            patient=request.user,
            appointment=appointment,
            title="Appointment Rescheduled",
            message=(
                f"Your appointment with "
                f"Dr. {appointment.doctor.name} "
                f"has been rescheduled to "
                f"{appointment.appointment_date} "
                f"at {appointment.appointment_time}."
            ),
            notification_type="appointment",
            reminder_type="general",
        )

        messages.success(
            request,
            "Appointment rescheduled successfully."
        )

        return redirect(
            "patient_dashboard"
        )

    return render(
        request,
        "patients/reschedule_appointment.html",
        {
            "appointment": appointment,
            "slots": slots,
            "selected_date": selected_date,
        }
    )


# Convert appointment date and time into timezone-aware datetime
def get_appt_datetime(appointment):

    naive_datetime = datetime.combine(
        appointment.appointment_date,
        appointment.appointment_time
    )

    return timezone.make_aware(
        naive_datetime,
        timezone.get_current_timezone()
    )


# Display all notifications
@login_required
def all_notifications(request):

    notifications = Notification.objects.filter(
        patient=request.user
    ).order_by(
        "-created_at"
    )

    return render(
        request,
        "patients/all_notifications.html",
        {
            "notifications": notifications
        }
    )

# Confirm attendance for a high no-show risk appointment
@login_required
def confirm_attendance(request, appointment_id):

    appointment = get_object_or_404(
        Appointment,
        appointment_id=appointment_id,
        patient=request.user
    )

    if request.method == "POST":

        # Only allow confirmation for upcoming appointments
        if appointment.status != "upcoming":

            messages.warning(
                request,
                "This appointment is no longer upcoming."
            )

            return redirect("patient_dashboard")

        # Confirm attendance
        appointment.attendance_confirmed = True

        appointment.save(
            update_fields=["attendance_confirmed"]
        )

        # Create dashboard notification
        create_notification(
            patient=request.user,
            appointment=appointment,
            title="Attendance Confirmed",
            message=(
                f"You have confirmed your attendance for your "
                f"appointment with Dr. {appointment.doctor.name} "
                f"on {appointment.appointment_date} "
                f"at {appointment.appointment_time}."
            ),
            notification_type="appointment",
            reminder_type="general",
        )

        # Send confirmation email
        patient = Patients.objects.filter(
            user=request.user
        ).first()

        if patient:

            send_notification_email(
                patient=patient,
                subject="Appointment Attendance Confirmed",
                message=(
                    f"Hello {patient.name},\n\n"
                    f"Your attendance has been confirmed for your "
                    f"appointment with Dr. {appointment.doctor.name} "
                    f"on {appointment.appointment_date} "
                    f"at {appointment.appointment_time}.\n\n"
                    "Thank you."
                )
            )

        messages.success(
            request,
            "Your attendance has been confirmed successfully."
        )

    return redirect("patient_dashboard")