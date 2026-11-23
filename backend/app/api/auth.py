from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.api.deps import CurrentUser, SessionDep
from app.core.security import (
    DUMMY_HASH,
    create_access_token,
    hash_password,
    verify_password,
)
from app.models import Token, User, UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, session: SessionDep):
    email = data.email.lower()

    existing = session.exec(select(User).where(User.email == email)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="এই ইমেইলে আগেই অ্যাকাউন্ট আছে",
        )

    user = User(email=email, hashed_password=hash_password(data.password))
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="এই ইমেইলে আগেই অ্যাকাউন্ট আছে",
        )
    session.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
):
    invalid_login = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="ইমেইল বা পাসওয়ার্ড ভুল",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = session.exec(
        select(User).where(User.email == form_data.username.lower())
    ).first()

    if user is None:
        verify_password(form_data.password, DUMMY_HASH)
        raise invalid_login

    if not verify_password(form_data.password, user.hashed_password):
        raise invalid_login

    return Token(access_token=create_access_token(str(user.id)))


@router.get("/me", response_model=UserRead)
def read_me(current_user: CurrentUser):
    return current_user