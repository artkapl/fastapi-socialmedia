from datetime import datetime
from sqlmodel import SQLModel, Field


class PostBase(SQLModel):
    title: str = Field(index=True)
    content: str = Field()
    published: bool = Field(default=True)


class PostSQL(PostBase, table=True):
    __tablename__: str = "posts_sql"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = Field(default=None)


class PostCreate(PostBase):
    pass


class PostUpdate(PostBase):
    pass
