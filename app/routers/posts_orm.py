from functools import lru_cache
from typing import Annotated

from fastapi import Depends, APIRouter, Query, status
from sqlmodel import Field, Session, SQLModel, create_engine, select

from app.config import Settings
from app.schema import PostRequest, PostSQL

################################
###   SQLMODEL ORM QUERIES   ###
################################


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()

psql_dialect = "postgresql+psycopg"
postgres_url = f"{psql_dialect}://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(postgres_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

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
