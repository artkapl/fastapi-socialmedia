from datetime import datetime
from pydantic import BaseModel

# Data classes for SQL Post Routes


class Post(BaseModel):
    id: int = None
    title: str
    content: str
    published: bool
    created_at: datetime = None
    updated_at: datetime | None = None


class PostRequest(BaseModel):
    title: str
    content: str
    published: bool
