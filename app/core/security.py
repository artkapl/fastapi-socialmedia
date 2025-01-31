import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from typing import Annotated, Any
from argon2 import PasswordHasher

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .config import get_settings
from app.models.auth import TokenData
from .database import SessionDep
from app.models.users import User


ph = PasswordHasher()
settings = get_settings()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

TokenDep = Annotated[str, Depends(oauth2_scheme)]


def verify_password(hashed_password: str, plain_password: str) -> bool:
    """Encode both plain and hashed Password strings as bytes and check PW with bcrypt."""
    return ph.verify(hashed_password, plain_password)


def get_password_hash(password: str) -> str:
    """Encode plain password string as bytes and hash with bcrypt."""
    return ph.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create JWT access Token"""
    # Set expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # get data to encode
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def get_current_user(
    session: SessionDep,
    token: TokenDep,
) -> User:
    """Return the currently logged in user or raise an UNAUTHORIZED exception."""
    token_data = verify_access_token(token)

    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def verify_access_token(token):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = TokenData(**payload)
    except InvalidTokenError:
        raise credentials_exception
    return token_data


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")
    return current_user
