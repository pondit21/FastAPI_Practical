NEW_STUDENT = {
    "email": "ayesha@example.com",
    "password": "Welcome123",
    "name": "Ayesha Siddiqua",
    "cgpa": 3.9,
    "class_name": "Class 9",
    "description": None,
    "start_date": "2024-01-10",
}


def create_by_admin(client, admin_headers, **overrides):
    return client.post(
        "/students", json={**NEW_STUDENT, **overrides}, headers=admin_headers
    )


def test_admin_creates_student_who_can_log_in(client, admin_headers):
    res = create_by_admin(client, admin_headers)
    assert res.status_code == 201
    assert res.json()["email"] == "ayesha@example.com"

    login = client.post(
        "/auth/login",
        data={"username": NEW_STUDENT["email"], "password": NEW_STUDENT["password"]},
    )
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    me = client.get("/auth/me", headers=headers)
    assert me.json()["role"] == "student"

    profile = client.get("/students/me", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["name"] == "Ayesha Siddiqua"


def test_admin_create_duplicate_email_rejected(client, admin_headers):
    create_by_admin(client, admin_headers)
    res = create_by_admin(client, admin_headers)
    assert res.status_code == 409


def test_student_cannot_create_students(client, student_headers):
    res = client.post("/students", json=NEW_STUDENT, headers=student_headers)
    assert res.status_code == 403


def test_admin_list_includes_email(client, admin_headers):
    create_by_admin(client, admin_headers)
    res = client.get("/students", headers=admin_headers)
    assert res.status_code == 200
    assert res.json()[0]["email"] == "ayesha@example.com"


def test_admin_get_one_and_missing(client, admin_headers):
    student_id = create_by_admin(client, admin_headers).json()["id"]
    assert client.get(f"/students/{student_id}", headers=admin_headers).status_code == 200
    assert client.get("/students/9999", headers=admin_headers).status_code == 404


def test_admin_can_put_student(client, admin_headers):
    student_id = create_by_admin(client, admin_headers).json()["id"]
    new_data = {
        "name": "Ayesha S.",
        "cgpa": 4.5,
        "class_name": "Class 10",
        "description": "Updated by admin",
        "start_date": "2024-02-01",
    }
    res = client.put(f"/students/{student_id}", json=new_data, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["name"] == "Ayesha S."
    assert res.json()["email"] == "ayesha@example.com"


def test_admin_can_patch_student(client, admin_headers):
    student_id = create_by_admin(client, admin_headers).json()["id"]
    res = client.patch(
        f"/students/{student_id}", json={"cgpa": 2.5}, headers=admin_headers
    )
    assert res.status_code == 200
    assert res.json()["cgpa"] == 2.5
    assert res.json()["name"] == "Ayesha Siddiqua"


def test_student_cannot_edit_via_admin_routes(
    client, student_headers, admin_headers, student_data
):
    student_id = create_by_admin(client, admin_headers).json()["id"]
    assert client.patch(
        f"/students/{student_id}", json={"cgpa": 1.0}, headers=student_headers
    ).status_code == 403
    assert client.put(
        f"/students/{student_id}", json=student_data, headers=student_headers
    ).status_code == 403
    assert client.get(f"/students/{student_id}", headers=student_headers).status_code == 403