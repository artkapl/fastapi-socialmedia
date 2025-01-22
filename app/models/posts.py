from sqlmodel import SQLModel, Field
from pydantic import EmailStr

from .models import BaseModel


class Posts(BaseModel, table=True):
    title: str = Field(index=True, nullable=False)
    content: str
    published: bool = Field(default=True, nullable=False)


class PostCreate(SQLModel):
    title: str
    content: str
    published: bool


class PostUpdate(PostCreate):
    pass
