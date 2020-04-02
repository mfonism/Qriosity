import gzip
import hashlib
import os
import re
from datetime import datetime, timedelta
from difflib import SequenceMatcher

import bcrypt
import jwt

from config import basedir, token_lifetime

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


def gen_access_token(uid):
    jwt_data = {
        "type": "access",
        "uid": uid,
        "exp": datetime.utcnow() + timedelta(seconds=token_lifetime),
    }
    jwt_token_bytes = jwt.encode(jwt_data, os.getenv("JWT_SECRET"), algorithm="HS256")
    return jwt_token_bytes.decode("utf-8")


def gen_refresh_token(uid, password_hash=None, request=None):
    if password_hash is None:
        assert request is not None
        # use request to get to db and fetch passsword hash

    jwt_data = {
        "type": "refresh",
        "uid": uid,
        "key": _gen_refresh_key(uid, password_hash),
    }
    jwt_token_bytes = jwt.encode(jwt_data, os.getenv("JWT_SECRET"), algorithm="HS256")
    return jwt_token_bytes.decode("utf-8")


def _gen_refresh_key(uid, password_hash):
    uid = str(uid)
    # prepend length of each parameter to the respective parameter
    # in the combo to guard against collisions
    combo = "{0}{1}{2}{3}".format(len(uid), uid, len(password_hash), password_hash)
    return hashlib.sha256(combo.encode("utf-8")).hexdigest()
