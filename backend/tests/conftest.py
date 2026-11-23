import os

# app import করার আগেই বসাতে হবে, যাতে টেস্ট কখনো আসল ডাটাবেসে না যায়
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret-key-only-for-pytest-0123456789"
os.environ["CORS_ORIGINS"] = "http://localhost:5173"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session, SQLModel, create_engine  # noqa: E402
from sqlmodel.pool import StaticPool  # noqa: E402

from app.core.security import hash_password  # noqa: E402
from app.db.session import get_session  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Role, User  # noqa: E402


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def create_student_user(client: TestClient):
    """নতুন student অ্যাকাউন্ট বানিয়ে লগইনের হেডার ফেরত দেয়"""

    def _create(email: str = "student@example.com", password: str = "Password123"):
        client.post("/auth/register", json={"email": email, "password": password})
        res = client.post(
            "/auth/login", data={"username": email, "password": password}
        )
        return {"Authorization": f"Bearer {res.json()['access_token']}"}

    return _create


@pytest.fixture
def student_headers(create_student_user):
    return create_student_user()


@pytest.fixture
def admin_headers(client: TestClient, session: Session):
    admin = User(
        email="admin@example.com",
        hashed_password=hash_password("AdminPass123"),
        role=Role.admin,
    )
    session.add(admin)
    session.commit()
    res = client.post(
        "/auth/login",
        data={"username": "admin@example.com", "password": "AdminPass123"},
    )
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


@pytest.fixture
def student_data():
    return {
        "name": "Rahim Uddin",
        "cgpa": 3.75,
        "class_name": "Class 10",
        "description": "Science student",
        "start_date": "2022-01-15",
    }