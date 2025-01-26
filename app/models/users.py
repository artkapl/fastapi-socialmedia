from sqlmodel import Field, Relationship, SQLModel
from pydantic import EmailStr


from .models import BaseModel


class User(BaseModel, table=True):
    __tablename__ = "users"

    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)
    email: EmailStr = Field(unique=True)
    password_crypt: str
    is_superuser: bool = False

    posts: list["Post"] = Relationship(back_populates="owner", cascade_delete=True)  # type: ignore


class UserCreate(SQLModel):
    email: EmailStr
    password: str


class UserUpdate(SQLModel):
    email: EmailStr | None = None
    password: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class UserPublic(BaseModel):
    email: EmailStr
    first_name: str | None
    last_name: str | None


class UserLogin(UserCreate):
    pass
