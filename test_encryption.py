from security.encryption import (
    generate_key,
    encrypt,
    decrypt
)


key = generate_key()

message = "Utsab Shrestha - 9801234567"

encrypted = encrypt(
    message,
    key
)

decrypted = decrypt(
    encrypted,
    key
)

print("Original:")
print(message)

print("\nEncrypted:")
print(encrypted)

print("\nDecrypted:")
print(decrypted)

print("\nMatch:")
print(message == decrypted)

tampered = encrypted[:-2] + "AA"

print("\nTesting tampered data:")

try:
    decrypt(
        tampered,
        key
    )

    print("Tampering was not detected.")

except ValueError as error:
    print("Tampering detected.")
    print(error)