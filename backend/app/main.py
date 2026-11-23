from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api import auth, bot, students
from app.core.config import settings
from app.db.session import engine

app = FastAPI(
    title="School Management API",
    version="1.1.0",
    description="Student management REST API with JWT authentication, profile photos and an FAQ assistant.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
app.include_router(students.router)
app.include_router(bot.router)


@app.get("/")
def root():
    return {"message": "School Management API চলছে"}


@app.get("/health/db")
def health_db():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"database": "connected"}