from sqlmodel import SQLModel, Field
from pydantic import EmailStr

from .models import BaseModel


class Post(BaseModel, table=True):
    __tablename__ = "posts"

    title: str = Field(index=True, nullable=False)
    content: str
    published: bool = Field(default=True, nullable=False)

    owner_id: int = Field(foreign_key="users.id")


class PostCreate(SQLModel):
    title: str
    content: str
    published: bool


class PostUpdate(PostCreate):
    pass
