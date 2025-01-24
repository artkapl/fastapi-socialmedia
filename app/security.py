from argon2 import PasswordHasher

ph = PasswordHasher()

def verify_password(hashed_password: str, plain_password: str) -> bool:
    """ Encode both plain and hashed Password strings as bytes and check PW with bcrypt. """
    return ph.verify(hashed_password, plain_password)


def get_password_hash(password: str) -> str:
    """ Encode plain password string as bytes and hash with bcrypt. """
    return ph.hash(password)
