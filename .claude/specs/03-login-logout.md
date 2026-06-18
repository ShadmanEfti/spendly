# Spec: Login and Logout

## Overview

Login and Logout turn Spendly's session-based authentication on. Login takes the
existing `GET /login` page and adds a `POST /login` handler that verifies an
email/password against the hashed credentials in the `users` table, then starts
a session by setting `session["user_id"]`. Logout replaces the current
placeholder route with one that clears the session and returns the visitor to a
public page. Together they complete the authentication loop started by
Registration (Step 2): a user can now sign in, stay signed in across requests,
and sign out — which is the prerequisite for every per-user feature that follows
(profile in Step 4, expense CRUD in Steps 7–9).

## Depends on

- **Step 1 — Database Setup**: the `users` table and the `get_db()` / `init_db()`
  helpers in `database/db.py`.
- **Step 2 — Registration**: accounts with werkzeug-hashed `password_hash`
  values must exist to log in against.

## Routes

- `GET /login` — render the sign-in form — public *(already exists)*
- `POST /login` — verify submitted credentials, start a session on success,
  re-render with an error on failure — public *(new handling on existing route)*
- `GET /logout` — clear the session and redirect to the landing/login page —
  logged-in *(currently a placeholder string)*

## Database changes

No database changes. The existing `users` table
(`id, name, email UNIQUE, password_hash, created_at`) already stores the hashed
password that login verifies against. Login reads only; logout touches no data.

## Templates

- **Create:** none.
- **Modify:**
  - `templates/login.html` — already POSTs to `/login` with `email` and
    `password` and already renders `{{ error }}`. No structural change required;
    only confirm the error block displays the message passed from the route.
  - `templates/base.html` *(optional)* — the navbar currently always shows
    "Sign in" / "Get started". Update it to show a "Logout" link
    (`{{ url_for('logout') }}`) when `session.get("user_id")` is set, so a
    signed-in user has a way to log out.

## Files to change

- `app.py` — allow `POST` on `/login` and add the credential-check handler;
  replace the `/logout` placeholder with a real handler that clears the session;
  add `session` (and `check_password_hash` from `werkzeug.security`) to the
  imports. `app.secret_key` is already set.
- `templates/base.html` — conditional navbar links (see Templates), if included.

## Files to create

- `tests/test_login.py` — tests for the login and logout flows.

## New dependencies

No new dependencies. Flask and Werkzeug are already in `requirements.txt`.

## Rules for implementation

- No SQLAlchemy or ORMs — use `get_db()` and raw SQL.
- Parameterised queries only — never string-interpolate user input.
- Passwords hashed with werkzeug — verify with `check_password_hash`; never
  compare plaintext and never log or echo passwords.
- Use CSS variables — never hardcode hex values (no restyling expected here).
- All templates extend `base.html` (`login.html` already does).
- Look the user up by email with a parameterised query, then verify the password
  against the stored `password_hash`.
- Use a single generic error message ("Invalid email or password.") for both an
  unknown email and a wrong password — do not reveal which one was wrong.
- On success, set `session["user_id"]` to the user's id and
  `redirect(url_for("profile"))`. (Profile is a placeholder until Step 4; the
  redirect target is correct now and the page fills in later.)
- On failure, re-render `login.html` with an `error` message and start no
  session.
- Logout must call `session.clear()` (or pop `user_id`) and redirect to a public
  page (`url_for("landing")` or `url_for("login")`).
- Currency context is taka (BDT) — no currency handling needed in this step.

## Definition of done

- `GET /login` returns the form (HTTP 200).
- Submitting a correct email/password pair sets `session["user_id"]` and
  redirects (302) to `/profile`.
- Submitting a wrong password or an unknown email re-renders the form (HTTP 200)
  with a visible generic error and sets no session.
- Submitting a blank email or password re-renders the form with a visible error
  and sets no session.
- `GET /logout` clears `session["user_id"]` and redirects (302) to a public page;
  after logout, session-protected behavior treats the visitor as signed out.
- The navbar shows a working "Logout" link while signed in (if the optional
  `base.html` change is included).
- `pytest tests/test_login.py` passes.
