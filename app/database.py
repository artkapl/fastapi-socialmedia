from functools import lru_cache
from typing import Annotated
from fastapi import Depends
from sqlmodel import Field, Session, create_engine, select

from app.config import Settings


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()

psql_dialect = "postgresql+psycopg"  # +psycopg is necessary for newer psycopg support (vs. default==psycopg2)
postgres_url = f"{psql_dialect}://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

engine = create_engine(postgres_url, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
def commit_and_refresh(session: SessionDep, record: SQLModel):
    session.commit()
    session.refresh(record)
