from datetime import datetime
from sqlmodel import SQLModel, Field


class PostSQL(SQLModel, table=True):
    __tablename__: str = "posts_sql"
    __table_args__ = {"extend_existing": True}

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    content: str | None = Field()
    published: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = Field()