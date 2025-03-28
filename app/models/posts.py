from sqlmodel import Relationship, SQLModel, Field
from pydantic import EmailStr

from .models import CreateUpdateTime
from .users import User, UserPublic


class Post(CreateUpdateTime, table=True):
    __tablename__ = "post"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True, nullable=False)
    content: str
    published: bool = Field(default=True, nullable=False)

    author_id: int = Field(foreign_key="user.id", ondelete="CASCADE")
    author: User = Relationship(back_populates="posts")


class PostCreate(SQLModel):
    title: str
    content: str
    published: bool


class PostUpdate(SQLModel):
    title: str | None = None
    content: str | None = None
    published: bool | None = None


class PostPublic(PostUpdate):
    id: int
    upvotes: int
    downvotes: int


class PostPublicWithUser(PostPublic):
    author: UserPublic | None = None
