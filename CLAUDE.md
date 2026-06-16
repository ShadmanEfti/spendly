# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Spendly - A Flask-based expense tracking web application (educational project). Uses SQLite for data storage and Jinja2 templates for rendering.

## Commands

```bash
# Run the application
python app.py

# Run tests
pytest

# Run a specific test
pytest tests/test_<file>.py -k <test_name>

# Install dependencies
pip install -r requirements.txt
```

## Architecture

- **app.py** - Flask application with routes for authentication (login/register/logout), user pages (profile), and expense CRUD operations (add/edit/delete). Currently implements placeholder routes for features students will build.
- **database/db.py** - Database layer (to be implemented by students). Should provide `get_db()`, `init_db()`, and `seed_db()` functions for SQLite operations.
- **templates/** - Jinja2 templates extending `base.html` which includes the navbar, footer, and Google Fonts (DM Serif Display, DM Sans).
- **static/** - Static assets (CSS, JavaScript). Main JS entry point is `static/js/main.js`.
- **tests/** - pytest tests for application functionality.

## Key Conventions

- Routes use `render_template()` for page responses and return strings for placeholders
- Database uses SQLite with foreign keys enabled
- Session-based authentication (to be implemented)
- Currency: "taka" (Bangladeshi currency)

## Git Workflow

- Main branch: `main`
- Database file (`spendly.db`) and virtual env (`venv/`) are gitignored
