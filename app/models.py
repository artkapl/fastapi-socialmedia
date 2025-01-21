from datetime import datetime
from sqlmodel import SQLModel, Field


class PostBase(SQLModel):
    title: str = Field(index=True, nullable=False)
    content: str = Field(nullable=False)
    published: bool = Field(default=True, nullable=False)


class PostSQL(PostBase, table=True):
    __tablename__: str = "posts_sql"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, title="Created Time in UTC")
    updated_at: datetime | None = Field(default=None, title="Time of Last Update in UTC")


class PostCreate(PostBase):
    pass


class PostUpdate(PostBase):
    pass
