from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Field, SQLModel, select

from app.api.deps import CurrentUser, SessionDep
from app.chatbot.faq import (
    FALLBACK_ANSWER,
    GREETING,
    find_answer,
    suggested_questions,
)
from app.models import Student

router = APIRouter(prefix="/bot", tags=["Bot"])


class BotQuestion(SQLModel):
    question: str = Field(min_length=1, max_length=300)


class BotAnswer(SQLModel):
    answer: str
    topic: str | None = None
    matched: bool


class BotTopics(SQLModel):
    greeting: str
    suggestions: list[str]


def require_student_profile(current_user: CurrentUser, session: SessionDep) -> Student:
    student = session.exec(
        select(Student).where(Student.user_id == current_user.id)
    ).first()
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bot ব্যবহার করতে আগে আপনার প্রোফাইল তৈরি করুন",
        )
    return student


StudentWithProfile = Annotated[Student, Depends(require_student_profile)]


@router.get("/topics", response_model=BotTopics)
def topics(_student: StudentWithProfile):
    return BotTopics(greeting=GREETING, suggestions=suggested_questions())


@router.post("/ask", response_model=BotAnswer)
def ask(data: BotQuestion, _student: StudentWithProfile):
    faq = find_answer(data.question)
    if faq is None:
        return BotAnswer(answer=FALLBACK_ANSWER, topic=None, matched=False)
    return BotAnswer(answer=faq.answer, topic=faq.topic, matched=True)