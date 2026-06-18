import pytest
from werkzeug.security import check_password_hash
from database.db import get_db, init_db


@pytest.fixture(autouse=True)
def setup(tmp_path, monkeypatch):
    monkeypatch.setattr("database.db.DB_PATH", str(tmp_path / "test.db"))
    init_db()


@pytest.fixture
def client():
    from app import app
    app.config["TESTING"] = True
    return app.test_client()


def _count_users():
    conn = get_db()
    n = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    return n


def test_get_register_returns_form(client):
    resp = client.get("/register")
    assert resp.status_code == 200


def test_valid_registration_creates_user_and_redirects(client):
    resp = client.post(
        "/register",
        data={
            "name": "Nitish Kumar",
            "email": "nitish@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")
    assert _count_users() == 1


def test_duplicate_email_rejected(client):
    data = {
        "name": "First",
        "email": "dupe@example.com",
        "password": "password123",
        "confirm_password": "password123",
    }
    client.post("/register", data=data)
    resp = client.post(
        "/register",
        data={
            "name": "Second",
            "email": "dupe@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )
    assert resp.status_code == 200
    assert b"already exists" in resp.data
    assert _count_users() == 1


def test_blank_field_rejected(client):
    resp = client.post(
        "/register",
        data={
            "name": "",
            "email": "blank@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )
    assert resp.status_code == 200
    assert b"All fields are required." in resp.data
    assert _count_users() == 0


def test_short_password_rejected(client):
    resp = client.post(
        "/register",
        data={
            "name": "Shorty",
            "email": "short@example.com",
            "password": "abc12",
            "confirm_password": "abc12",
        },
    )
    assert resp.status_code == 200
    assert b"at least 8 characters" in resp.data
    assert _count_users() == 0


def test_password_mismatch_rejected(client):
    resp = client.post(
        "/register",
        data={
            "name": "Mismatch",
            "email": "mismatch@example.com",
            "password": "password123",
            "confirm_password": "password999",
        },
    )
    assert resp.status_code == 200
    assert b"Passwords do not match." in resp.data
    assert _count_users() == 0


def test_password_is_hashed_not_plaintext(client):
    client.post(
        "/register",
        data={
            "name": "Hash Me",
            "email": "hash@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )
    conn = get_db()
    row = conn.execute(
        "SELECT password_hash FROM users WHERE email = ?", ("hash@example.com",)
    ).fetchone()
    conn.close()
    assert row["password_hash"] != "password123"
    assert check_password_hash(row["password_hash"], "password123")
