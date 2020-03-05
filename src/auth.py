import re

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


def validate_password(pwd):
    return all([len(pwd) >= 8 and len(pwd) <= 64])
