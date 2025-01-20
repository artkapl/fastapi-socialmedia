from functools import lru_cache
from typing import Annotated

from fastapi import Depends, APIRouter, HTTPException, Query, status
from sqlmodel import Field, create_engine, select, SQLModel
from app.database import SessionDep, engine

from app.models import PostSQL, PostCreate

################################
###   SQLMODEL ORM QUERIES   ###
################################


router = APIRouter(prefix="/sqlmodel/posts")


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@router.on_event("startup")
def on_startup():
    create_db_and_tables()
    print("SQLModel: Created DB and Tables.")


@router.get("/", response_model=list[PostSQL])
async def get_posts_paginated(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    posts = await session.exec(select(PostSQL).offset(offset).limit(limit)).all()
    return posts


@router.get(
    "/{id}", response_model=PostSQL, responses={404: {"description": "Not Found"}}
)
def get_post(id: int, session: SessionDep):
    post = session.get(PostSQL, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostSQL)
def create_post(post: PostCreate, session: SessionDep):
    # Convert PostRequest to Post in DB
    db_post = PostSQL.model_validate(post)
    # Store Post in DB
    session.add(db_post)
    session.commit()
    return db_post
