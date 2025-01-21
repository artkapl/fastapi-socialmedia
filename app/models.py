from datetime import datetime
from sqlmodel import SQLModel, Field


class Posts(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True, nullable=False)
    content: str = Field(nullable=False)
    published: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, title="Created Time in UTC")
    updated_at: datetime | None = Field(default=None, title="Time of Last Update in UTC")


class PostCreate(SQLModel):
    title: str = Field(index=True, nullable=False)
    content: str = Field(nullable=False)
    published: bool = Field(default=True, nullable=False)


class PostUpdate(PostCreate):
    pass
