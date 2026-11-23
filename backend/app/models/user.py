from enum import Enum
from typing import TYPE_CHECKING, Optional

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.student import Student


class Role(str, Enum):
    admin = "admin"
    student = "student"


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    hashed_password: str
    role: Role = Field(default=Role.student)

    student: Optional["Student"] = Relationship(back_populates="user")


# ---------- API-র জন্য schema (ডাটাবেসে টেবিল হয় না) ----------

class UserCreate(SQLModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserRead(SQLModel):
    id: int
    email: str
    role: Role


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"