from typing import Annotated
import argon2
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from app.core import security
from app.core.database import SessionDep
from app.models.auth import Token
from app.models.users import User


router = APIRouter(tags=["Authentication"])


@router.post("/login")
def login_user(login_form: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep) -> Token:
    user = session.exec(select(User).where(User.email == login_form.username)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    try:
        security.verify_password(user.password_crypt, login_form.password)
    except argon2.exceptions.VerifyMismatchError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    # Create token
    access_token = security.create_access_token({"sub": str(user.id)})

    # return token
    return Token(access_token=access_token, token_type="bearer")
