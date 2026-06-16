import sqlite3

DB_PATH = "spendly.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS expenses (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            amount     REAL    NOT NULL,
            category   TEXT    NOT NULL,
            date       TEXT    NOT NULL,
            note       TEXT,
            created_at TEXT    NOT NULL DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()


def seed_db():
    from werkzeug.security import generate_password_hash
    conn = get_db()

    conn.execute(
        "INSERT OR IGNORE INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo user", "demo@example.com", generate_password_hash("password123")),
    )
    conn.commit()

    demo = conn.execute("SELECT id FROM users WHERE email = 'demo@example.com'").fetchone()
    sample_expenses = [
        (demo["id"], 120.00,  "Food",          "2026-06-10", "Rice + curry"),
        (demo["id"], 80.00,   "Transport",     "2026-06-11", None),
        (demo["id"], 450.00,  "Groceries",     "2026-06-12", "Weekly groceries"),
        (demo["id"], 600.00,  "Utilities",     "2026-06-13", "Monthly broadband"),
        (demo["id"], 250.00,  "Entertainment", "2026-06-14", "Cinema with friends"),
        (demo["id"], 50.00,   "Transport",     "2026-06-15", None),
        (demo["id"], 380.00,  "Health",        "2026-06-15", "Pharmacy"),
        (demo["id"], 850.00,  "Shopping",      "2026-06-16", "Bashundhara City"),
    ]
    conn.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, note) VALUES (?,?,?,?,?)",
        sample_expenses,
    )
    conn.commit()
    conn.close()
