import io

from PIL import Image


def make_image(fmt="PNG", size=(1200, 800)):
    buf = io.BytesIO()
    Image.new("RGB", size, (30, 120, 200)).save(buf, format=fmt)
    return buf.getvalue()


def png_upload():
    return {"file": ("me.png", make_image(), "image/png")}


def test_upload_and_download_photo(client, student_headers, student_data):
    client.post("/students/me", json=student_data, headers=student_headers)

    res = client.put("/students/me/photo", files=png_upload(), headers=student_headers)
    assert res.status_code == 200
    assert res.json()["has_photo"] is True

    photo = client.get("/students/me/photo", headers=student_headers)
    assert photo.status_code == 200
    assert photo.headers["content-type"] == "image/jpeg"
    width, height = Image.open(io.BytesIO(photo.content)).size
    assert max(width, height) <= 512


def test_photo_before_upload_returns_404(client, student_headers, student_data):
    client.post("/students/me", json=student_data, headers=student_headers)
    assert client.get("/students/me/photo", headers=student_headers).status_code == 404


def test_non_image_rejected(client, student_headers, student_data):
    client.post("/students/me", json=student_data, headers=student_headers)
    res = client.put(
        "/students/me/photo",
        files={"file": ("note.txt", b"just text", "text/plain")},
        headers=student_headers,
    )
    assert res.status_code == 400


def test_oversized_file_rejected(client, student_headers, student_data):
    client.post("/students/me", json=student_data, headers=student_headers)
    big = b"0" * (5 * 1024 * 1024 + 10)
    res = client.put(
        "/students/me/photo",
        files={"file": ("big.png", big, "image/png")},
        headers=student_headers,
    )
    assert res.status_code == 413


def test_photo_requires_profile_and_login(client, student_headers):
    assert client.put("/students/me/photo", files=png_upload()).status_code == 401
    res = client.put("/students/me/photo", files=png_upload(), headers=student_headers)
    assert res.status_code == 404


def test_delete_photo(client, student_headers, student_data):
    client.post("/students/me", json=student_data, headers=student_headers)
    client.put("/students/me/photo", files=png_upload(), headers=student_headers)

    res = client.delete("/students/me/photo", headers=student_headers)
    assert res.status_code == 200
    assert res.json()["has_photo"] is False
    assert client.get("/students/me/photo", headers=student_headers).status_code == 404


def test_admin_can_set_and_read_student_photo(
    client, student_headers, admin_headers, student_data
):
    student_id = client.post(
        "/students/me", json=student_data, headers=student_headers
    ).json()["id"]

    res = client.put(
        f"/students/{student_id}/photo", files=png_upload(), headers=admin_headers
    )
    assert res.status_code == 200
    assert res.json()["has_photo"] is True

    assert client.get(f"/students/{student_id}/photo", headers=admin_headers).status_code == 200
    assert client.get(f"/students/{student_id}/photo", headers=student_headers).status_code == 403


def test_deleting_student_also_removes_photo(
    client, student_headers, admin_headers, student_data
):
    student_id = client.post(
        "/students/me", json=student_data, headers=student_headers
    ).json()["id"]
    client.put("/students/me/photo", files=png_upload(), headers=student_headers)

    res = client.delete(f"/students/{student_id}", headers=admin_headers)
    assert res.status_code == 204