from django.db import models
from django.contrib.auth.models import User
from doctors.models import Doctor

from security.encryption import encrypt, decrypt
from security.key import ENCRYPTION_KEY


class Appointment(models.Model):

    appointment_id = models.AutoField(primary_key=True)

    appointment_date = models.DateField()
    appointment_time = models.TimeField()

    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('missed', 'Missed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    # Appointment approval/rejection
    APPROVAL_CHOICES = [
        ("approved", "Approved"),
        ("review", "Needs Review"),
        ("rejected", "Rejected"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='upcoming'
    )

    approval_status = models.CharField(
        max_length=20,
        choices=APPROVAL_CHOICES,
        default="approved",
    )

    review_reason = models.CharField(
        max_length=255,
        blank=True,
    )

    no_show_probability = models.FloatField(
        null=True,
        blank=True
    )

    no_show_prediction = models.BooleanField(
        null=True,
        blank=True
    )

    attendance_confirmed = models.BooleanField(
        default=False
    )

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = (
            'doctor',
            'appointment_date',
            'appointment_time'
        )

    def __str__(self):
        return (
            f"{self.patient} - {self.doctor} - "
            f"{self.appointment_date} {self.appointment_time}"
        )


class MedicalReport(models.Model):

    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE
    )

    # Temporary fields used by the Django form.
    # These are cleared before the database record is saved.
    diagnosis = models.TextField(
        blank=True
    )

    prescription = models.TextField(
        blank=True
    )

    remarks = models.TextField(
        blank=True
    )

    # Encrypted database values
    encrypted_diagnosis = models.TextField(
        blank=True,
        null=True
    )

    encrypted_prescription = models.TextField(
        blank=True,
        null=True
    )

    encrypted_remarks = models.TextField(
        blank=True,
        null=True
    )

    # Original uploaded file field.
    # This will be used temporarily during upload.
    report_file = models.FileField(
        upload_to="reports/",
        blank=True,
        null=True
    )

    # Encrypted uploaded file data
    encrypted_report_file = models.TextField(
        blank=True,
        null=True
    )

    # Original filename, e.g. report.jpg
    report_original_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):

        

        # Encrypt diagnosis
        if self.diagnosis:
            self.encrypted_diagnosis = encrypt(
                self.diagnosis,
                ENCRYPTION_KEY
            )

        # Encrypt prescription
        if self.prescription:
            self.encrypted_prescription = encrypt(
                self.prescription,
                ENCRYPTION_KEY
            )

        # Encrypt remarks
        if self.remarks:
            self.encrypted_remarks = encrypt(
                self.remarks,
                ENCRYPTION_KEY
            )

        # Encrypt uploaded file
        if self.report_file:

            self.report_file.seek(0)

            file_data = self.report_file.read()

            self.encrypted_report_file = encrypt(
                file_data,
                ENCRYPTION_KEY
            )

            self.report_original_name = self.report_file.name

            # Do NOT store the plaintext file
            self.report_file = None

        # Remove plaintext medical text
        self.diagnosis = ""
        self.prescription = ""
        self.remarks = ""

        super().save(*args, **kwargs)

    def decrypt_data(self):

        # Decrypt diagnosis
        if self.encrypted_diagnosis:
            self.diagnosis = decrypt(
                self.encrypted_diagnosis,
                ENCRYPTION_KEY
            )

        # Decrypt prescription
        if self.encrypted_prescription:
            self.prescription = decrypt(
                self.encrypted_prescription,
                ENCRYPTION_KEY
            )

        # Decrypt remarks
        if self.encrypted_remarks:
            self.remarks = decrypt(
                self.encrypted_remarks,
                ENCRYPTION_KEY
            )

        return self

    def __str__(self):
        return (
            f"Report - "
            f"{self.appointment.patient.username}"
        )