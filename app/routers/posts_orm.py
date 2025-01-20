from functools import lru_cache
from typing import Annotated

from fastapi import Depends, APIRouter, Query, status
from sqlmodel import Field, create_engine, select
from app.database import SessionDep, create_db_and_tables

from app.schema import PostRequest, PostSQL

################################
###   SQLMODEL ORM QUERIES   ###
################################


router = APIRouter(prefix="/sqlmodel/posts")


@router.on_event("startup")
def on_startup():
    create_db_and_tables()
    print("SQLModel: Created DB and Tables.")


@router.get("/")
def read_posts_paginated(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[PostSQL]:
    posts = session.exec(select(PostSQL).offset(offset).limit(limit)).all()
    return posts


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_post(post_request: PostRequest, session: SessionDep) -> PostSQL:
    # Convert PostRequest to Post in DB
    post = PostSQL(
        title=post_request.title,
        content=post_request.content,
        published=post_request.published,
    )

    # Store Post in DB
    session.add(post)
    session.commit()
    return post
