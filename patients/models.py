from django.db import models
from django.contrib.auth.models import User


class Patients(models.Model):
    patient_id = models.AutoField(primary_key=True)

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    name = models.CharField(
        max_length=150
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    address = models.CharField(
        max_length=150
    )

    phone = models.CharField(
        max_length=10
    )

    dob = models.DateField()

    Gender_Choices = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "Other"),
    ]

    gender = models.CharField(
        max_length=1,
        choices=Gender_Choices
    )

    encrypted_name = models.TextField(
        blank=True,
        null=True
    )

    encrypted_email = models.TextField(
        blank=True,
        null=True
    )

    encrypted_address = models.TextField(
        blank=True,
        null=True
    )

    encrypted_phone = models.TextField(
        blank=True,
        null=True
    )

    encrypted_dob = models.TextField(
        blank=True,
        null=True
    )

    encrypted_gender = models.TextField(
        blank=True,
        null=True
    )

    phone_lookup = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        db_index=True
    )

    email_lookup = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        db_index=True
    )