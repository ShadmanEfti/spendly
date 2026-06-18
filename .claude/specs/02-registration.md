# Spec: Registration

## Overview

Registration lets a new visitor create a Spendly account by submitting their
name, email, and password. It turns the existing `GET /register` placeholder
into a full sign-up flow: validate the submission, store the user with a
securely hashed password, start a logged-in session, and send them into the
app. This is the first feature to write to the `users` table created in Step 1,
and it unlocks login/logout (Step 3) and every per-user feature after it.

## Depends on

- **Step 1 — Database Setup**: the `users` table and the `get_db()` / `init_db()`
  helpers in `database/db.py` must exist.

## Routes

- `GET /register` — render the registration form — public
- `POST /register` — process the submitted form, create the user, start a
  session, and redirect to the profile page — public

(The `GET /register` route already exists; it gains `POST` handling.)

## Database changes

No database changes. The existing `users` table
(`id, name, email UNIQUE, password_hash, created_at`) in `database/db.py`
already covers everything registration needs. `created_at` is populated by its
column default and must not be set manually.

## Templates

- **Create:** none.
- **Modify:** `templates/register.html` — already POSTs to `/register` with the
  fields `name`, `email`, `password` and already renders `{{ error }}`. No
  structural change is required; only confirm the error block displays the
  message passed from the route.

## Files to change

- `app.py` — allow `POST` on `/register`, add the registration handler, set
  `app.secret_key`, and import `request`, `redirect`, `url_for`, `session` from
  `flask` plus `generate_password_hash` from `werkzeug.security` and `get_db`
  from `database.db`.

## Files to create

- `tests/test_register.py` — tests for the registration flow.

## New dependencies

No new dependencies. Flask and Werkzeug are already in `requirements.txt`.

## Rules for implementation

- No SQLAlchemy or ORMs — use `get_db()` and raw SQL.
- Parameterised queries only — never string-interpolate user input.
- Passwords hashed with werkzeug (`generate_password_hash`); never store plaintext.
- Use CSS variables — never hardcode hex values (no template restyling expected here).
- All templates extend `base.html` (`register.html` already does).
- Server-side validation: all fields required (non-empty after `strip()`),
  password at least 8 characters, email must be unique.
- On any validation failure, re-render `register.html` with an `error` message
  and create no user row.
- On success, set `session["user_id"]` to the new user's id (`cursor.lastrowid`)
  and `redirect(url_for("profile"))`.
- Currency context is taka (BDT) — no currency handling needed in this step.

## Definition of done

- `GET /register` returns the form (HTTP 200).
- Submitting valid, unique details creates exactly one row in `users`, stores a
  hashed (not plaintext) password, sets `session["user_id"]`, and redirects
  (302) to `/profile`.
- Submitting an email that already exists re-renders the form with a visible
  error and adds no new row.
- Submitting a blank field or a password shorter than 8 characters re-renders
  the form with a visible error and adds no new row.
- `pytest tests/test_register.py` passes, including a check that the stored
  `password_hash` does not equal the submitted plaintext password.
