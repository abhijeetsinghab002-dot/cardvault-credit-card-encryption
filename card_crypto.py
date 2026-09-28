import base64
import os
import re
import uuid

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class CardError(ValueError):
    pass


def normalize_pan(value):
    pan = re.sub(r"[ -]", "", value or "")
    if not pan.isdigit() or not 12 <= len(pan) <= 19:
        raise CardError("Card number must contain 12–19 digits.")
    if not luhn_valid(pan):
        raise CardError("Card number failed the Luhn validation check.")
    return pan


def luhn_valid(pan):
    total = 0
    parity = len(pan) % 2
    for index, digit in enumerate(map(int, pan)):
        if index % 2 == parity:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def mask_pan(pan):
    return "*" * (len(pan) - 4) + pan[-4:]


def new_token():
    return "tok_" + uuid.uuid4().hex


class CardCipher:
    def __init__(self, key):
        if len(key) != 32:
            raise ValueError("AES-256 requires a 32-byte key.")
        self.aes = AESGCM(key)

    def encrypt(self, pan, token):
        nonce = os.urandom(12)
        ciphertext = self.aes.encrypt(nonce, pan.encode(), token.encode())
        return base64.urlsafe_b64encode(nonce + ciphertext).decode()

    def decrypt(self, payload, token):
        raw = base64.urlsafe_b64decode(payload.encode())
        return self.aes.decrypt(raw[:12], raw[12:], token.encode()).decode()
