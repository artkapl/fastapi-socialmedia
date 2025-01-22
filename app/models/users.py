from sqlmodel import Field
from pydantic import EmailStr

from .models import BaseModel


class Users(BaseModel, table=True):
    first_name: str | None = Field()
    last_name: str | None = Field()
    email: EmailStr = Field(unique=True)
    password: str = Field(nullable=False)
