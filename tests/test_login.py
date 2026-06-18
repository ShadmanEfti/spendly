import pytest
from werkzeug.security import generate_password_hash
from database.db import get_db, init_db


@pytest.fixture(autouse=True)
def setup(tmp_path, monkeypatch):
    monkeypatch.setattr("database.db.DB_PATH", str(tmp_path / "test.db"))
    init_db()
    _seed_user("rofi@example.com", "password123")


@pytest.fixture
def client():
    from app import app
    app.config["TESTING"] = True
    return app.test_client()


def _seed_user(email, password):
    conn = get_db()
    conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Rofi", email, generate_password_hash(password)),
    )
    conn.commit()
    conn.close()


def test_get_login_returns_form(client):
    resp = client.get("/login")
    assert resp.status_code == 200


def test_valid_login_sets_session_and_redirects(client):
    resp = client.post(
        "/login",
        data={"email": "rofi@example.com", "password": "password123"},
        follow_redirects=False,
    )
    assert resp.status_code == 302
    assert resp.headers["Location"] in ("/", "http://localhost/")
    with client.session_transaction() as sess:
        assert sess.get("user_id") is not None


def test_wrong_password_rejected(client):
    resp = client.post(
        "/login",
        data={"email": "rofi@example.com", "password": "wrongpass"},
    )
    assert resp.status_code == 200
    assert b"Invalid email or password." in resp.data
    with client.session_transaction() as sess:
        assert sess.get("user_id") is None


def test_unknown_email_rejected(client):
    resp = client.post(
        "/login",
        data={"email": "nobody@example.com", "password": "password123"},
    )
    assert resp.status_code == 200
    assert b"Invalid email or password." in resp.data
    with client.session_transaction() as sess:
        assert sess.get("user_id") is None


def test_blank_email_rejected(client):
    resp = client.post(
        "/login",
        data={"email": "", "password": "password123"},
    )
    assert resp.status_code == 200
    assert b"Invalid email or password." in resp.data
    with client.session_transaction() as sess:
        assert sess.get("user_id") is None


def test_blank_password_rejected(client):
    resp = client.post(
        "/login",
        data={"email": "rofi@example.com", "password": ""},
    )
    assert resp.status_code == 200
    assert b"Invalid email or password." in resp.data
    with client.session_transaction() as sess:
        assert sess.get("user_id") is None


def test_login_page_redirects_when_logged_in(client):
    client.post(
        "/login",
        data={"email": "rofi@example.com", "password": "password123"},
    )
    resp = client.get("/login", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["Location"] in ("/", "http://localhost/")


def test_register_page_redirects_when_logged_in(client):
    client.post(
        "/login",
        data={"email": "rofi@example.com", "password": "password123"},
    )
    resp = client.get("/register", follow_redirects=False)
    assert resp.status_code == 302
    assert resp.headers["Location"] in ("/", "http://localhost/")


def test_logout_clears_session_and_redirects(client):
    client.post(
        "/login",
        data={"email": "rofi@example.com", "password": "password123"},
    )
    resp = client.get("/logout", follow_redirects=False)
    assert resp.status_code == 302
    with client.session_transaction() as sess:
        assert sess.get("user_id") is None
