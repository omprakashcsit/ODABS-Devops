import hashlib
import hmac
from datetime import date

from security.encryption import encrypt, decrypt


def create_lookup(value, key):
    value = value.strip().lower().encode("utf-8")

    return hmac.new(
        key,
        value,
        hashlib.sha256
    ).hexdigest()


def encrypt_patient_data(patient, key):
    patient.encrypted_name = encrypt(
        patient.name,
        key
    )

    patient.encrypted_email = encrypt(
        patient.email or "",
        key
    )

    patient.encrypted_address = encrypt(
        patient.address,
        key
    )

    patient.encrypted_phone = encrypt(
        patient.phone,
        key
    )

    patient.encrypted_dob = encrypt(
        patient.dob.isoformat(),
        key
    )

    patient.encrypted_gender = encrypt(
        patient.gender,
        key
    )

    patient.phone_lookup = create_lookup(
        patient.phone,
        key
    )

    patient.email_lookup = create_lookup(
        patient.email or "",
        key
    )


def decrypt_patient_data(patient, key):
    patient.name = decrypt(
        patient.encrypted_name,
        key
    )

    patient.email = decrypt(
        patient.encrypted_email,
        key
    )

    patient.address = decrypt(
        patient.encrypted_address,
        key
    )

    patient.phone = decrypt(
        patient.encrypted_phone,
        key
    )

    decrypted_dob = decrypt(
        patient.encrypted_dob,
        key
    )

    patient.dob = date.fromisoformat(
        decrypted_dob
    )

    patient.gender = decrypt(
        patient.encrypted_gender,
        key
    )

    return patient