import base64
import hashlib
import hmac
import secrets



# AES-256 CONSTANTS



S_BOX = [
    0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
    0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
    0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
    0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
    0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
    0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
    0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
    0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
    0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
    0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
    0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
    0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
    0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
    0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
    0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
    0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16
]

RCON = [
    0x00,
    0x01,
    0x02,
    0x04,
    0x08,
    0x10,
    0x20,
    0x40,
    0x80,
    0x1B,
    0x36
]



# AES BASIC OPERATIONS


def add_round_key(state, round_key):

    for i in range(16):
        state[i] ^= round_key[i]

    return state


def sub_bytes(state):

    for i in range(16):
        state[i] = S_BOX[state[i]]

    return state


def shift_rows(state):

    state[1], state[5], state[9], state[13] = (
        state[5],
        state[9],
        state[13],
        state[1]
    )

    state[2], state[6], state[10], state[14] = (
        state[10],
        state[14],
        state[2],
        state[6]
    )

    state[3], state[7], state[11], state[15] = (
        state[15],
        state[3],
        state[7],
        state[11]
    )

    return state


def galois_multiply(a, b):

    result = 0

    for _ in range(8):

        if b & 1:
            result ^= a

        high_bit = a & 0x80

        a = (a << 1) & 0xFF

        if high_bit:
            a ^= 0x1B

        b >>= 1

    return result


def mix_columns(state):

    for column in range(4):

        i = column * 4

        a0 = state[i]
        a1 = state[i + 1]
        a2 = state[i + 2]
        a3 = state[i + 3]

        state[i] = (
            galois_multiply(a0, 2)
            ^ galois_multiply(a1, 3)
            ^ a2
            ^ a3
        )

        state[i + 1] = (
            a0
            ^ galois_multiply(a1, 2)
            ^ galois_multiply(a2, 3)
            ^ a3
        )

        state[i + 2] = (
            a0
            ^ a1
            ^ galois_multiply(a2, 2)
            ^ galois_multiply(a3, 3)
        )

        state[i + 3] = (
            galois_multiply(a0, 3)
            ^ a1
            ^ a2
            ^ galois_multiply(a3, 2)
        )

    return state


# KEY EXPANSION


def rotate_word(word):

    return word[1:] + word[:1]


def sub_word(word):

    return [S_BOX[value] for value in word]


def expand_key(key):

    if len(key) != 32:
        raise ValueError(
            "AES-256 key must be exactly 32 bytes."
        )

    words = []

    for i in range(8):

        words.append(
            list(
                key[i * 4:(i + 1) * 4]
            )
        )

    for i in range(8, 60):

        temp = words[i - 1].copy()

        if i % 8 == 0:

            temp = rotate_word(temp)
            temp = sub_word(temp)

            temp[0] ^= RCON[i // 8]

        elif i % 8 == 4:

            temp = sub_word(temp)

        new_word = []

        for j in range(4):

            new_word.append(
                words[i - 8][j] ^ temp[j]
            )

        words.append(new_word)

    round_keys = []

    for round_number in range(15):

        round_key = []

        for word in words[
            round_number * 4:
            round_number * 4 + 4
        ]:

            round_key.extend(word)

        round_keys.append(round_key)

    return round_keys



# AES BLOCK ENCRYPTION


def aes_encrypt_block(block, round_keys):

    if len(block) != 16:
        raise ValueError(
            "AES block must be 16 bytes."
        )

    state = list(block)

    state = add_round_key(
        state,
        round_keys[0]
    )

    for round_number in range(1, 15):

        state = sub_bytes(state)

        state = shift_rows(state)

        if round_number != 14:
            state = mix_columns(state)

        state = add_round_key(
            state,
            round_keys[round_number]
        )

    return bytes(state)



# AES BLOCK DECRYPTION


def create_inverse_s_box():

    inverse_s_box = [0] * 256

    for index, value in enumerate(S_BOX):

        inverse_s_box[value] = index

    return inverse_s_box


INVERSE_S_BOX = create_inverse_s_box()


def inv_sub_bytes(state):

    for i in range(16):

        state[i] = INVERSE_S_BOX[state[i]]

    return state


def inv_shift_rows(state):

    state[1], state[5], state[9], state[13] = (
        state[13],
        state[1],
        state[5],
        state[9]
    )

    state[2], state[6], state[10], state[14] = (
        state[10],
        state[14],
        state[2],
        state[6]
    )

    state[3], state[7], state[11], state[15] = (
        state[7],
        state[11],
        state[15],
        state[3]
    )

    return state


def inv_mix_columns(state):

    for column in range(4):

        i = column * 4

        a0 = state[i]
        a1 = state[i + 1]
        a2 = state[i + 2]
        a3 = state[i + 3]

        state[i] = (
            galois_multiply(a0, 14)
            ^ galois_multiply(a1, 11)
            ^ galois_multiply(a2, 13)
            ^ galois_multiply(a3, 9)
        )

        state[i + 1] = (
            galois_multiply(a0, 9)
            ^ galois_multiply(a1, 14)
            ^ galois_multiply(a2, 11)
            ^ galois_multiply(a3, 13)
        )

        state[i + 2] = (
            galois_multiply(a0, 13)
            ^ galois_multiply(a1, 9)
            ^ galois_multiply(a2, 14)
            ^ galois_multiply(a3, 11)
        )

        state[i + 3] = (
            galois_multiply(a0, 11)
            ^ galois_multiply(a1, 13)
            ^ galois_multiply(a2, 9)
            ^ galois_multiply(a3, 14)
        )

    return state


def aes_decrypt_block(block, round_keys):

    if len(block) != 16:
        raise ValueError(
            "AES block must be 16 bytes."
        )

    state = list(block)

    state = add_round_key(
        state,
        round_keys[14]
    )

    for round_number in range(13, 0, -1):

        state = inv_shift_rows(state)

        state = inv_sub_bytes(state)

        state = add_round_key(
            state,
            round_keys[round_number]
        )

        state = inv_mix_columns(state)

    state = inv_shift_rows(state)

    state = inv_sub_bytes(state)

    state = add_round_key(
        state,
        round_keys[0]
    )

    return bytes(state)



# PKCS#7


def pad(data):

    padding_length = 16 - (
        len(data) % 16
    )

    return data + bytes(
        [padding_length] * padding_length
    )


def unpad(data):

    if not data:
        raise ValueError(
            "Invalid padded data."
        )

    padding_length = data[-1]

    if (
        padding_length < 1
        or padding_length > 16
    ):
        raise ValueError(
            "Invalid padding."
        )

    if data[-padding_length:] != bytes(
        [padding_length] * padding_length
    ):
        raise ValueError(
            "Invalid padding."
        )

    return data[:-padding_length]



# XOR


def xor_blocks(block1, block2):

    return bytes(
        a ^ b
        for a, b in zip(block1, block2)
    )


# AES CBC ENCRYPTION


def aes_cbc_encrypt(data, key, iv):

    if len(key) != 32:
        raise ValueError(
            "AES-256 key must be 32 bytes."
        )

    if len(iv) != 16:
        raise ValueError(
            "IV must be 16 bytes."
        )

    round_keys = expand_key(key)

    data = pad(data)

    encrypted = []

    previous_block = iv

    for position in range(
        0,
        len(data),
        16
    ):

        block = data[
            position:position + 16
        ]

        block = xor_blocks(
            block,
            previous_block
        )

        encrypted_block = aes_encrypt_block(
            block,
            round_keys
        )

        encrypted.append(
            encrypted_block
        )

        previous_block = encrypted_block

    return b"".join(encrypted)



# AES CBC DECRYPTION


def aes_cbc_decrypt(data, key, iv):

    if len(key) != 32:
        raise ValueError(
            "AES-256 key must be 32 bytes."
        )

    if len(iv) != 16:
        raise ValueError(
            "IV must be 16 bytes."
        )

    if (
        len(data) == 0
        or len(data) % 16 != 0
    ):
        raise ValueError(
            "Invalid ciphertext length."
        )

    # IMPORTANT:
    # Expand the key ONLY ONCE.
    round_keys = expand_key(key)

    decrypted = []

    previous_block = iv

    for position in range(
        0,
        len(data),
        16
    ):

        block = data[
            position:position + 16
        ]

        decrypted_block = aes_decrypt_block(
            block,
            round_keys
        )

        decrypted_block = xor_blocks(
            decrypted_block,
            previous_block
        )

        decrypted.append(
            decrypted_block
        )

        previous_block = block

    return unpad(
        b"".join(decrypted)
    )



# HMAC-SHA256


def create_hmac(key, data):

    return hmac.new(
        key,
        data,
        hashlib.sha256
    ).digest()



# ENCRYPT


def encrypt(data, key):

    if isinstance(data, str):

        data = data.encode(
            "utf-8"
        )

    if not isinstance(data, bytes):

        raise TypeError(
            "Data must be bytes or string."
        )

    if len(key) != 32:

        raise ValueError(
            "Encryption key must be 32 bytes."
        )

    # Generate random IV
    iv = secrets.token_bytes(16)

    ciphertext = aes_cbc_encrypt(
        data,
        key,
        iv
    )

    # HMAC protects IV + ciphertext
    authentication_data = (
        iv + ciphertext
    )

    tag = create_hmac(
        key,
        authentication_data
    )

    package = (
        iv
        + ciphertext
        + tag
    )

    return base64.b64encode(
        package
    ).decode("utf-8")


# DECRYPT


def decrypt(encrypted_data, key, binary=False):

    if len(key) != 32:
        raise ValueError(
            "Decryption key must be 32 bytes."
        )

    try:
        package = base64.b64decode(
            encrypted_data,
            validate=True
        )
    except Exception as error:
        raise ValueError(
            "Invalid encrypted data."
        ) from error

    if len(package) < 48:
        raise ValueError(
            "Invalid encrypted package."
        )

    iv = package[:16]

    tag = package[-32:]

    ciphertext = package[16:-32]

    authentication_data = iv + ciphertext

    expected_tag = create_hmac(
        key,
        authentication_data
    )

    if not hmac.compare_digest(
        tag,
        expected_tag
    ):
        raise ValueError(
            "HMAC verification failed."
        )

    plaintext = aes_cbc_decrypt(
        ciphertext,
        key,
        iv
    )

    if binary:
        return plaintext

    return plaintext.decode("utf-8")


# KEY GENERATION

def generate_key():

    return secrets.token_bytes(32)