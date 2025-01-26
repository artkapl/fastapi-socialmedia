from sqlmodel import Relationship, SQLModel, Field
from pydantic import EmailStr

from .models import BaseModel
from .users import User


class Post(BaseModel, table=True):
    __tablename__ = "posts"

    title: str = Field(index=True, nullable=False)
    content: str
    published: bool = Field(default=True, nullable=False)

    owner_id: int = Field(foreign_key="users.id", ondelete="CASCADE")
    owner: User = Relationship(back_populates="posts")


class PostCreate(SQLModel):
    title: str
    content: str
    published: bool


class PostUpdate(PostCreate):
    pass
