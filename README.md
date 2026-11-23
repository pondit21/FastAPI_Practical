# School Management System

A full-stack school management application. Students create an account, log in, and manage their own profile; admins can view all students and remove records. Built with a REST API backend (FastAPI) and a React frontend.

> **Status:** Backend complete. Frontend (React + Tailwind CSS) in progress.

## Features

- JWT authentication (register / login) with Argon2 password hashing
- Role-based access control: `student` and `admin`
- Students can create, read, fully update (PUT) and partially update (PATCH) **only their own** profile
- Only admins can list all students and delete records
- Input validation (CGPA range, email format, password length)
- Database migrations with Alembic
- Automated test suite (pytest)
- Auto-generated interactive API docs (Swagger UI)

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, SQLModel |
| Database | PostgreSQL |
| Auth | JWT (PyJWT), Argon2 (pwdlib) |
| Migrations | Alembic |
| Testing | pytest, httpx |
| Tooling | uv |
| Frontend (planned) | React, Tailwind CSS |
| Deployment (planned) | Vercel (frontend), managed PostgreSQL |

## API Overview

| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/auth/register` | Public | Create a student account |
| POST | `/auth/login` | Public | Log in, receive a JWT |
| GET | `/auth/me` | Logged in | Current user info |
| POST | `/students/me` | Student | Create own profile |
| GET | `/students/me` | Student | Get own profile |
| PUT | `/students/me` | Student | Replace own profile |
| PATCH | `/students/me` | Student | Partially update own profile |
| GET | `/students` | Admin | List all students (paginated) |
| DELETE | `/students/{id}` | Admin | Delete a student profile |

Student fields: `id`, `name`, `cgpa`, `class_name`, `description`, `start_date`.

## Project Structure

```
school-management/
├── backend/
│   ├── app/
│   │   ├── api/         # routes (auth, students) and dependencies
│   │   ├── core/        # settings and security (JWT, hashing)
│   │   ├── db/          # database engine and session
│   │   ├── models/      # SQLModel tables and schemas
│   │   └── main.py
│   ├── migrations/      # Alembic migrations
│   ├── scripts/         # create_admin.py
│   └── tests/
└── frontend/            # React app (in progress)
```

## Getting Started

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- PostgreSQL

### Setup

```bash
git clone https://github.com/<pondit21>/school-management.git
cd school-management/backend

# install dependencies
uv sync

# create the database
psql -U postgres -c "CREATE DATABASE school_db;"

# configure environment
cp .env.example .env
# edit .env: set your DB password and a SECRET_KEY
# generate a key with:
#   uv run python -c "import secrets; print(secrets.token_hex(32))"

# create tables
uv run alembic upgrade head

# create an admin user
uv run python -m scripts.create_admin

# run the API
uv run uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs for the interactive API documentation.

### Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | Secret used to sign JWTs |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime (default 60) |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins |

### Running Tests

```bash
uv run pytest -v
```

Tests run against an in-memory SQLite database, so they never touch your real data.

## Security Notes

- Passwords are hashed with Argon2 and never returned by the API
- Users cannot choose their own role at registration; admins are created via a CLI script
- Students can only access their own profile; the profile owner comes from the JWT, never from the request body
- Login errors are generic to avoid revealing which emails are registered

## Roadmap

- [x] REST API with authentication and roles
- [x] Migrations and tests
- [ ] React + Tailwind frontend
- [ ] Deployment

- Profile photos (validated, resized and stored in PostgreSQL)
- Built-in FAQ assistant: each student gets their own chat, answers come from a shared knowledge base
- Admins can create student accounts and edit any student's data


- Profile photos with server-side validation and resizing
- Floating FAQ assistant for every student with a profile
- Admin can create student accounts, edit details and manage photos