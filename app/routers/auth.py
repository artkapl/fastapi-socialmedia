from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.database import SessionDep
from app.models.users import User, UserLogin
from app.security import verify_password


router = APIRouter(tags=["Authentication"])

router.post("/login")
def login_user(login: UserLogin, session: SessionDep):

    user = session.exec(select(User).where(User.email == login.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email or password are not correct")
    
    pass_correct = verify_password(login.password, user.password_crypt)
    if not pass_correct:
        raise HTTPException(status_code=404, detail="Email or password are not correct")

    # Create token

    # return token
