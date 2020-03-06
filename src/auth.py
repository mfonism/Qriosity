import gzip
import re
from difflib import SequenceMatcher

import bcrypt

from config import basedir

email_username_regex = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*\Z"
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"\Z)',  # noqa
    re.IGNORECASE,
)

email_domain_regex = re.compile(
    r"((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+)(?:[A-Z0-9-]{2,63}(?<!-))\Z",
    re.IGNORECASE,
)


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


def _check_password_similarity(password, other):
    for part in re.split(r"\W+", other) + [other]:
        if SequenceMatcher(a=password, b=part).quick_ratio() >= 0.7:
            return False
    return True


def _check_password_commonness(password):
    with gzip.open(
        basedir.joinpath("common-passwords.txt.gz"), "rt", encoding="utf-8"
    ) as file:
        for line in file:
            if password == line.strip():
                return False
    return True


def validate_password(password, username, email):
    """
    Validate a password against a username and an email.

    Return True if password is not strongly similar to either of the rest.
    """
    password = password.lower()
    username = username.lower()
    email.lower()
    return all(
        [
            len(password) >= 8,
            len(password) <= 64,
            password not in username,
            username not in password,
            email not in password,
            password not in email,
            _check_password_similarity(password, username),
            _check_password_similarity(password, email),
            _check_password_commonness(password),
        ]
    )


def validate_email(email):
    if "@" not in email:
        return False

    username, domain = email.rsplit("@", 1)

    return email_username_regex.match(username) and email_domain_regex.match(domain)
