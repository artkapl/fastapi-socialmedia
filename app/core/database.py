from typing import Annotated
from fastapi import Depends
from sqlmodel import SQLModel, Session, create_engine

from . import config

settings = config.get_settings()

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI), echo=True)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def commit_and_refresh(session: SessionDep, record: SQLModel):
    session.commit()
    session.refresh(record)
