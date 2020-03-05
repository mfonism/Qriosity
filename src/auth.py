import re
from difflib import SequenceMatcher

import bcrypt


def get_password_hash(plaintext, workfactor=13):
    byte_encoded_plaintext = plaintext.encode("utf-8")
    byte_encoded_hash = bcrypt.hashpw(
        byte_encoded_plaintext, bcrypt.gensalt(workfactor)
    )
    return byte_encoded_hash.decode("utf-8")


def check_password_hash(plaintext, hash):
    byte_encoded_plaintext = plaintext.encode("utf-8")
    byte_encoded_hash = hash.encode("utf-8")
    return bcrypt.checkpw(byte_encoded_plaintext, byte_encoded_hash)


def validate_username(name):
    return all([re.compile(r"^[\w.@+-]+\Z").search(name), len(name) > 4])


def _get_similarity_ratio(pwd, other):
    for part in re.split(r"\W+", other) + [other]:
        if SequenceMatcher(a=pwd, b=part).quick_ratio() >= 0.7:
            return False
    return True


def validate_password(pwd, username, email):
    """
    Validate a password against a username and an email.

    Return True if password is not strongly similar to either of the rest.
    """
    pwd = pwd.lower()
    username = username.lower()
    email.lower()
    return all(
        [
            len(pwd) >= 8,
            len(pwd) <= 64,
            pwd not in username,
            username not in pwd,
            email not in pwd,
            pwd not in email,
            _get_similarity_ratio(pwd, username),
            _get_similarity_ratio(pwd, email),
        ]
    )
