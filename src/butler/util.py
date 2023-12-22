# Ref: https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import base64
import os


def derive_key(salt: bytes, pw: bytes) -> bytes:
    """Derive encryption key using a password and salt"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000)
    return base64.urlsafe_b64encode(kdf.derive(pw))


def hash_pw(pw: bytes) -> tuple:
    """Convenience function to hash a password"""
    salt = os.urandom(16)
    return salt, derive_key(salt, pw)


def encrypt_wrapper(root_pw: bytes, secret: bytes) -> tuple:
    """Symmetrically encrypt a secret and return the token and salt"""
    salt = os.urandom(16)
    token = encrypt_with_salt(root_pw, salt, secret)
    return token, salt


def encrypt_with_salt(root_pw: bytes, salt: bytes, secret: bytes) -> bytes:
    """Symmetrically encrypt a secret with root password and salt"""
    key = derive_key(salt, root_pw)
    f = Fernet(key)
    return f.encrypt(secret)


def decrypt_with_salt(root_pw: bytes, salt: bytes, token: bytes) -> bytes:
    """Decrypt a token"""
    key = derive_key(salt, root_pw)
    f = Fernet(key)
    return f.decrypt(token)

