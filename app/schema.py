from datetime import datetime
from pydantic import BaseModel


class Post(BaseModel):
    id: int = None
    title: str
    content: str
    published: bool
    created_at: datetime = None
    updated_at: datetime = None
