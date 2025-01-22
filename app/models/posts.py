from sqlmodel import SQLModel, Field
from pydantic import EmailStr

from .models import BaseModel


class Posts(BaseModel, table=True):
    title: str = Field(index=True, nullable=False)
    content: str = Field(nullable=False)
    published: bool = Field(default=True, nullable=False)


class PostCreate(SQLModel):
    title: str = Field(index=True, nullable=False)
    content: str = Field()
    published: bool = Field(default=True)


class PostUpdate(PostCreate):
    pass
