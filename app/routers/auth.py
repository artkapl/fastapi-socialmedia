import argon2
from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.database import SessionDep
from app.models.users import User, UserLogin
from app.security import verify_password, create_access_token


router = APIRouter(tags=["Authentication"])


@router.post("/login")
def login_user(login: UserLogin, session: SessionDep):
    user = session.exec(select(User).where(User.email == login.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Invalid Credentials")

    try:
        verify_password(user.password_crypt, login.password)
    except argon2.exceptions.VerifyMismatchError:
        raise HTTPException(status_code=404, detail="Invalid Credentials")

    # Create token
    access_token = create_access_token(user.id)

    # return token
    return {"token": access_token}
