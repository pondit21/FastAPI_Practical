from datetime import date
from typing import TYPE_CHECKING, Optional

from pydantic import EmailStr
from sqlalchemy import Column, LargeBinary, false
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user import User


class StudentBase(SQLModel):
    name: str = Field(min_length=2, max_length=100)
    cgpa: float = Field(ge=0, le=5)
    class_name: str = Field(max_length=50)
    description: str | None = Field(default=None, max_length=1000)
    start_date: date


class Student(StudentBase, table=True):
    __tablename__ = "students"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True, index=True)
    has_photo: bool = Field(
        default=False,
        sa_column_kwargs={"server_default": false()},
    )

    user: Optional["User"] = Relationship(back_populates="student")
    photo: Optional["StudentPhoto"] = Relationship(
        back_populates="student",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "uselist": False},
    )


class StudentPhoto(SQLModel, table=True):
    __tablename__ = "student_photos"

    student_id: int = Field(foreign_key="students.id", primary_key=True)
    data: bytes = Field(sa_column=Column(LargeBinary, nullable=False))

    student: Optional["Student"] = Relationship(back_populates="photo")


# ---------- API-র জন্য schema ----------

class StudentCreate(StudentBase):
    """নতুন প্রোফাইল তৈরি (POST) ও পুরো আপডেট (PUT)"""


class StudentUpdate(SQLModel):
    """আংশিক আপডেট (PATCH): সব ফিল্ড ঐচ্ছিক"""
    name: str | None = Field(default=None, min_length=2, max_length=100)
    cgpa: float | None = Field(default=None, ge=0, le=5)
    class_name: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=1000)
    start_date: date | None = None


class StudentRead(StudentBase):
    id: int
    user_id: int
    has_photo: bool = False


class StudentAdminRead(StudentRead):
    """শুধু admin-এর জন্য: সাথে অ্যাকাউন্টের ইমেইল"""
    email: str


class AdminStudentCreate(StudentCreate):
    """admin নতুন student বানানোর সময়: অ্যাকাউন্ট + প্রোফাইল একসাথে"""
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)