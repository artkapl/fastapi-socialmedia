from datetime import datetime, timedelta, timezone
from typing import Any
from argon2 import PasswordHasher
import jwt

from app.config import get_settings

ALGORITHM = "HS256"

ph = PasswordHasher()
settings = get_settings()


def verify_password(hashed_password: str, plain_password: str) -> bool:
    """Encode both plain and hashed Password strings as bytes and check PW with bcrypt."""
    return ph.verify(hashed_password, plain_password)


def get_password_hash(password: str) -> str:
    """Encode plain password string as bytes and hash with bcrypt."""
    return ph.hash(password)


def create_access_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    """Create JWT access Token"""
    # Set expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    try:
        subject_string = str(subject)
    except Exception as e:
        raise ValueError(f"JWT Encoding Error: Subject can not be parsed into a string.")

    to_encode = {"exp": expire, "sub": subject_string}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
