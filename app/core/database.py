from typing import Annotated
from fastapi import Depends
from sqlmodel import SQLModel, Session, create_engine

from . import config

settings = config.get_settings()

postgres_url = f"{settings.PSQL_DIALECT}://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

engine = create_engine(postgres_url, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def commit_and_refresh(session: SessionDep, record: SQLModel):
    session.commit()
    session.refresh(record)
