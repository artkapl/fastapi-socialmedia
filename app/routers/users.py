from datetime import UTC, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlmodel import select
from app.core.database import SessionDep, commit_and_refresh
from app.core.security import CurrentUser, get_current_user, get_password_hash

from app.models.users import UserCreate, User, UserPublic, UserUpdate


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserPublic])
def get_users_paginated(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[User]:
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


@router.get("/{id}", response_model=UserPublic)
def get_user(id: int, session: SessionDep) -> User:
    user = session.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found!")
    return user


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserPublic)
def create_user(user: UserCreate, session: SessionDep) -> User:
    # Hash Password
    password_crypt = {"password_crypt": get_password_hash(user.password)}
    # Convert PostCreate object to Post in DB
    db_user = User.model_validate(user, update=password_crypt)
    # Store Post in DB
    session.add(db_user)
    commit_and_refresh(session, db_user)
    return db_user


@router.patch("/{id}", response_model=UserPublic)
def update_user(user: UserUpdate, id: int, session: SessionDep, current_user: CurrentUser) -> User:
    db_user = session.get(User, id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found!")

    # Extract only fields that were changed
    user_data = user.model_dump(exclude_unset=True)

    # Hash Password if PW was updated
    extra_data = {}
    if "password" in user_data:
        hashed_pw = get_password_hash(user.password)
        extra_data["password_crypt"] = hashed_pw

    db_user.sqlmodel_update(user_data, update=extra_data)
    db_user.updated_at = datetime.now(UTC)
    session.add(db_user)
    commit_and_refresh(session, db_user)
    return db_user


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, session: SessionDep, current_user: CurrentUser) -> Response:
    db_user = session.get(User, id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found!")
    # if not current_user.is_superuser or current_user.id != db_user.id:
    # raise 403
    session.delete(db_user)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
