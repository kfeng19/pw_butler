import logging
import os
import pickle

from butler.util import derive_key, hash_pw

AUTH_PATH = os.path.expanduser("~/.pw_butler/auth.bin")


def initialize(pw: bytes, auth_file=AUTH_PATH) -> None:
    """Initialize the authentication file"""
    salt, pw_hash = hash_pw(pw)
    with open(auth_file, "wb") as f:
        pickle.dump((salt, pw_hash), f)
    logging.info("Root password initialized.")


def verify_password(pw: bytes, auth_file=AUTH_PATH) -> bool:
    """Authenticate given password"""
    if not os.path.isfile(auth_file):
        raise FileNotFoundError("Please initialize authentication first!")
    with open(auth_file, "rb") as f:
        salt, pw_hash = pickle.load(f)
    new_hash = derive_key(salt, pw)
    return new_hash == pw_hash
