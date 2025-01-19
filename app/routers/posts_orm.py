from datetime import datetime
from functools import lru_cache
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, APIRouter, Query
from sqlalchemy import func
from sqlmodel import Field, Session, SQLModel, create_engine, select, DateTime

from ..config import Settings

################################
###   SQLMODEL ORM QUERIES   ###
################################


@lru_cache
def get_settings():
    return Settings()

settings = get_settings()

class PostSQL(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    content: str | None = Field()
    published: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)  # todo: timestamp WITH tz
    updated_at: datetime | None = Field()

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

router = APIRouter(
    prefix="/sqlmodel/posts"
)

@router.on_event("startup")
def on_startup():
    create_db_and_tables()
    print("SQLModel: Created DB and Tables.")


@router.get("/")
def read_posts(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[PostSQL]:
    posts = session.exec(select(PostSQL).offset(offset).limit(limit)).all()
    return posts

@router.post("/")
def create_post(post: PostSQL, session: SessionDep):
    session.add(post)
    session.commit()
    # session.refresh(post)
    return post
