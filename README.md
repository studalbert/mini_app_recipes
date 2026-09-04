# Recipe Mini App

Telegram Mini App for sharing recipes: public feed, search, photos, private drafts, and a personal cookbook of saved dishes.

Users open the app inside Telegram. Identity comes from signed WebApp `initData` — no passwords, no JWT.

| Package | Role |
| --- | --- |
| [`recipe-app-backend`](./recipe-app-backend) | FastAPI + PostgreSQL API |
| [`recipe-app-frontend`](./recipe-app-frontend) | React + Vite Mini App UI |

## What it demonstrates

- Telegram Mini App auth (HMAC validation of `initData`, replay window)
- Async REST API (FastAPI, SQLAlchemy 2.0, Alembic)
- Ownership and visibility (author-only edits, public vs private)
- File uploads with signature-based type checks
- SPA for Telegram WebView (routing, search debounce, haptics)

## Quick start

1. Start PostgreSQL and the API — see [backend README](./recipe-app-backend/README.md).
2. Start the Vite app — see [frontend README](./recipe-app-frontend/README.md).
3. For a desktop browser, generate `initData` with `recipe-app-backend/scripts/generate_test_init_data.py` and put it in `recipe-app-frontend/.env` as `VITE_DEV_INIT_DATA`.

Open [http://localhost:5173](http://localhost:5173) with the API at [http://localhost:8000](http://localhost:8000).


