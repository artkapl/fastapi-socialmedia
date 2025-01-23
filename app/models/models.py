from datetime import datetime
from sqlmodel import SQLModel, Field


class BaseModel(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow, 
        nullable=False, 
        description="Created Time in UTC")
    updated_at: datetime | None = Field(
        default=None, 
        description="Time of Last Update in UTC")