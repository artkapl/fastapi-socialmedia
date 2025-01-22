from typing import Annotated
from fastapi import APIRouter, Query, status
from sqlmodel import select
from app.database import SessionDep, commit_and_refresh

from app.models.users import UserCreate, User


router = APIRouter(prefix="/users")

@router.get("/", response_model=list[User])
def get_users_paginated(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=User)
def create_user(user: UserCreate, session: SessionDep):
    # Convert PostCreate object to Post in DB
    db_user = User.model_validate(user)
    # Store Post in DB
    session.add(db_user)
    commit_and_refresh(session, db_user)
    return db_user
