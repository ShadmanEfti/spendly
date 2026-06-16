# Step 1 — Database Setup

## Goal

Wire up the SQLite database layer so all later steps (auth, CRUD) have a working foundation.

## Requirements

### `database/db.py`

Implement three functions:

- **`get_db()`** — opens a connection to `spendly.db`, sets `row_factory = sqlite3.Row` so rows behave like dicts, enables foreign keys with `PRAGMA foreign_keys = ON`, and returns the connection.
- **`init_db()`** — creates the `users` and `expenses` tables using `CREATE TABLE IF NOT EXISTS` (safe to call multiple times).
- **`seed_db()`** — inserts sample users and expenses for development. Uses `INSERT OR IGNORE` so re-running does not duplicate data.

### Schema

**users**

| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| name | TEXT | NOT NULL |
| email | TEXT | NOT NULL UNIQUE |
| password_hash | TEXT | NOT NULL |
| created_at | TEXT | NOT NULL DEFAULT (datetime('now')) |

**expenses**

| Column | Type | Constraints |
|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| user_id | INTEGER | NOT NULL, REFERENCES users(id) ON DELETE CASCADE |
| amount | REAL | NOT NULL |
| category | TEXT | NOT NULL |
| date | TEXT | NOT NULL |
| note | TEXT | nullable |
| created_at | TEXT | NOT NULL DEFAULT (datetime('now')) |

### `app.py`

- Import `init_db` from `database.db`.
- Call `init_db()` inside the `if __name__ == "__main__":` block before `app.run()` so the database file is created on app startup.

### Tests (`tests/test_db.py`)

Cover:
- `get_db()` returns a `sqlite3.Connection` with `row_factory` set.
- Foreign keys are enabled on the connection.
- `init_db()` creates both tables.
- `seed_db()` inserts at least 2 users and 5 expenses.

Use `monkeypatch` to redirect `DB_PATH` to a temp file so tests don't touch the real database.

## Verification

```bash
python app.py          # starts server and creates spendly.db in project root
pytest                 # all 4 tests pass
sqlite3 spendly.db ".tables"   # prints: expenses  users
```
