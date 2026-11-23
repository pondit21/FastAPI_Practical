def test_root(client):
    res = client.get("/")
    assert res.status_code == 200


def test_cors_allows_frontend_origin(client):
    res = client.options(
        "/students/me",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert res.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_blocks_unknown_origin(client):
    res = client.options(
        "/students/me",
        headers={
            "Origin": "http://evil.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" not in res.headers