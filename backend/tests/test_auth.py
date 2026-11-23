def test_register_success(client):
    res = client.post(
        "/auth/register",
        json={"email": "new@example.com", "password": "Password123"},
    )
    assert res.status_code == 201
    body = res.json()
    assert body["email"] == "new@example.com"
    assert body["role"] == "student"
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_duplicate_email(client):
    payload = {"email": "dup@example.com", "password": "Password123"}
    client.post("/auth/register", json=payload)
    res = client.post("/auth/register", json=payload)
    assert res.status_code == 409


def test_register_short_password_rejected(client):
    res = client.post(
        "/auth/register",
        json={"email": "short@example.com", "password": "123"},
    )
    assert res.status_code == 422


def test_register_cannot_choose_admin_role(client):
    res = client.post(
        "/auth/register",
        json={
            "email": "sneaky@example.com",
            "password": "Password123",
            "role": "admin",
        },
    )
    assert res.status_code == 201
    assert res.json()["role"] == "student"


def test_login_success(client, create_student_user):
    create_student_user("login@example.com")
    res = client.post(
        "/auth/login",
        data={"username": "login@example.com", "password": "Password123"},
    )
    assert res.status_code == 200
    assert res.json()["token_type"] == "bearer"
    assert res.json()["access_token"]


def test_login_wrong_password(client, create_student_user):
    create_student_user("wrong@example.com")
    res = client.post(
        "/auth/login",
        data={"username": "wrong@example.com", "password": "WrongPassword"},
    )
    assert res.status_code == 401


def test_login_unknown_email(client):
    res = client.post(
        "/auth/login",
        data={"username": "ghost@example.com", "password": "Password123"},
    )
    assert res.status_code == 401


def test_me_requires_token(client):
    assert client.get("/auth/me").status_code == 401


def test_me_returns_current_user(client, student_headers):
    res = client.get("/auth/me", headers=student_headers)
    assert res.status_code == 200
    assert res.json()["email"] == "student@example.com"