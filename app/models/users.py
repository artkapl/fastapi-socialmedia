from sqlmodel import Field, SQLModel
from pydantic import EmailStr

from .models import BaseModel


class Users(BaseModel, table=True):
    first_name: str | None = Field()
    last_name: str | None = Field()
    email: EmailStr = Field(unique=True)
    username: str
    password: str

class UserCreate(SQLModel):
    email: EmailStr
    password: str
