def test_create_profile(client, student_headers, student_data):
    res = client.post("/students/me", json=student_data, headers=student_headers)
    assert res.status_code == 201
    body = res.json()
    assert body["name"] == "Rahim Uddin"
    assert body["cgpa"] == 3.75
    assert "id" in body and "user_id" in body


def test_create_profile_twice_rejected(client, student_headers, student_data):
    client.post("/students/me", json=student_data, headers=student_headers)
    res = client.post("/students/me", json=student_data, headers=student_headers)
    assert res.status_code == 409


def test_create_profile_invalid_cgpa(client, student_headers, student_data):
    student_data["cgpa"] = 6
    res = client.post("/students/me", json=student_data, headers=student_headers)
    assert res.status_code == 422


def test_profile_endpoints_require_login(client, student_data):
    assert client.get("/students/me").status_code == 401
    assert client.post("/students/me", json=student_data).status_code == 401
    assert client.put("/students/me", json=student_data).status_code == 401
    assert client.patch("/students/me", json={"cgpa": 3.0}).status_code == 401


def test_get_profile_before_creating_returns_404(client, student_headers):
    res = client.get("/students/me", headers=student_headers)
    assert res.status_code == 404


def test_get_my_profile(client, student_headers, student_data):
    client.post("/students/me", json=student_data, headers=student_headers)
    res = client.get("/students/me", headers=student_headers)
    assert res.status_code == 200
    assert res.json()["name"] == "Rahim Uddin"


def test_student_sees_only_own_profile(
    client, create_student_user, student_headers, student_data
):
    client.post("/students/me", json=student_data, headers=student_headers)
    other_headers = create_student_user("other@example.com")
    res = client.get("/students/me", headers=other_headers)
    assert res.status_code == 404


def test_put_replaces_profile(client, student_headers, student_data):
    client.post("/students/me", json=student_data, headers=student_headers)
    new_data = {
        "name": "Karim Hossain",
        "cgpa": 4.0,
        "class_name": "Class 11",
        "description": None,
        "start_date": "2023-02-01",
    }
    res = client.put("/students/me", json=new_data, headers=student_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["name"] == "Karim Hossain"
    assert body["class_name"] == "Class 11"
    assert body["description"] is None


def test_patch_updates_only_sent_fields(client, student_headers, student_data):
    client.post("/students/me", json=student_data, headers=student_headers)
    res = client.patch("/students/me", json={"cgpa": 3.9}, headers=student_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["cgpa"] == 3.9
    assert body["name"] == "Rahim Uddin"
    assert body["class_name"] == "Class 10"


def test_patch_empty_body_rejected(client, student_headers, student_data):
    client.post("/students/me", json=student_data, headers=student_headers)
    res = client.patch("/students/me", json={}, headers=student_headers)
    assert res.status_code == 400


def test_patch_null_required_field_rejected(client, student_headers, student_data):
    client.post("/students/me", json=student_data, headers=student_headers)
    res = client.patch("/students/me", json={"name": None}, headers=student_headers)
    assert res.status_code == 422


def test_student_cannot_list_students(client, student_headers):
    res = client.get("/students", headers=student_headers)
    assert res.status_code == 403


def test_admin_can_list_students(
    client, student_headers, admin_headers, student_data
):
    client.post("/students/me", json=student_data, headers=student_headers)
    res = client.get("/students", headers=admin_headers)
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_student_cannot_delete(client, student_headers, student_data):
    created = client.post("/students/me", json=student_data, headers=student_headers)
    student_id = created.json()["id"]
    res = client.delete(f"/students/{student_id}", headers=student_headers)
    assert res.status_code == 403


def test_admin_can_delete_student(
    client, student_headers, admin_headers, student_data
):
    created = client.post("/students/me", json=student_data, headers=student_headers)
    student_id = created.json()["id"]

    res = client.delete(f"/students/{student_id}", headers=admin_headers)
    assert res.status_code == 204

    again = client.delete(f"/students/{student_id}", headers=admin_headers)
    assert again.status_code == 404

    mine = client.get("/students/me", headers=student_headers)
    assert mine.status_code == 404