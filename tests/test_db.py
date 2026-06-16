import sqlite3
import pytest
from database.db import get_db, init_db, seed_db


@pytest.fixture(autouse=True)
def use_tmp_db(tmp_path, monkeypatch):
    monkeypatch.setattr("database.db.DB_PATH", str(tmp_path / "test.db"))


def test_get_db_returns_connection():
    conn = get_db()
    assert isinstance(conn, sqlite3.Connection)
    assert conn.row_factory is sqlite3.Row
    conn.close()


def test_foreign_keys_enabled():
    conn = get_db()
    result = conn.execute("PRAGMA foreign_keys").fetchone()
    assert result[0] == 1
    conn.close()


def test_init_db_creates_tables():
    init_db()
    conn = get_db()
    tables = {r["name"] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    assert "users" in tables
    assert "expenses" in tables
    conn.close()


def test_seed_db_inserts_data():
    init_db()
    seed_db()
    conn = get_db()
    assert conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] >= 1
    assert conn.execute("SELECT COUNT(*) FROM expenses").fetchone()[0] >= 5
    conn.close()
