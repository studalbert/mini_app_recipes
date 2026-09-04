# Recipe Mini App — API

Backend for a **Telegram Mini App** where users publish recipes, browse a public feed, and save other people’s dishes. Auth is Telegram `initData` (HMAC), not a custom JWT.

This service is the API for [`recipe-app-frontend`](../recipe-app-frontend).

## Features

- Telegram WebApp auth: HMAC-SHA256 validation of `initData`, 24h replay window, auto-provision of users
- Recipe CRUD with ingredients, cooking steps, and public / private visibility
- Public feed with title search (results ranked by save count)
- Save / unsave others’ recipes; “my recipes” and “saved” lists
- Image upload (JPEG / PNG / WebP), type check by file signature, size and count limits
- User profile with recipe and saved counts
- Async PostgreSQL via SQLAlchemy 2.0 + Alembic migrations
- OpenAPI / Swagger at `/docs`

## Tech stack

| Layer | Choice |
| --- | --- |
| API | FastAPI, Pydantic v2 |
| ORM | SQLAlchemy 2.0 (async), asyncpg |
| DB | PostgreSQL, Alembic |
| Auth | Telegram Mini App `initData` |
| Files | Local disk, served at `/uploads` |
| Config | pydantic-settings, `.env` |

## Auth

Protected routes expect:

```http
Authorization: tma <initData>
```

`initData` is signed by Telegram. The server rebuilds `data_check_string`, computes HMAC with the bot token, and rejects a missing/invalid hash or stale payload. There is no session cookie and no JWT: each request carries `initData`.

Locally, generate a valid string with `scripts/generate_test_init_data.py` (needs a real `TELEGRAM_BOT_TOKEN` from [@BotFather](https://t.me/BotFather)).

## API surface

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/health` | Liveness |
| `GET` | `/auth/me` | Current user (creates row on first visit) |
| `GET` | `/profile` | Profile + counts |
| `GET` | `/recipes` | Public feed (`q`, `limit`, `offset`) |
| `POST` | `/recipes` | Create recipe |
| `GET` | `/recipes/my` | Own recipes |
| `GET` | `/recipes/saved` | Saved recipes |
| `GET` | `/recipes/{id}` | Recipe detail |
| `PUT` | `/recipes/{id}` | Update (author only) |
| `DELETE` | `/recipes/{id}` | Delete (author only) |
| `POST` | `/recipes/{id}/save` | Save |
| `DELETE` | `/recipes/{id}/save` | Unsave |
| `POST` | `/recipes/{id}/images` | Upload photos |
| `DELETE` | `/recipes/{id}/images/{image_id}` | Delete photo |

Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Project layout

```
recipe-app-backend/
├── app/
│   ├── main.py           # FastAPI app, CORS, static uploads
│   ├── config.py         # env settings
│   ├── database.py       # async engine / session
│   ├── security.py       # Telegram initData HMAC
│   ├── dependencies.py   # get_current_user
│   ├── storage.py        # image validation and disk I/O
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic DTOs
│   └── routers/          # auth, profile, recipes
├── alembic/              # migrations
├── scripts/
│   └── generate_test_init_data.py
├── requirements.txt
└── .env.example
```

## Data model

- **User** — Telegram id, username, name, photo
- **Recipe** — title, cooking text, `is_public`, author
- **Ingredient** — ordered lines per recipe
- **RecipeImage** — relative file path + position
- **SavedRecipe** — unique (user, recipe)

Private recipes stay out of the feed; they remain reachable by id.

## Run locally

**1. PostgreSQL** (Docker example; compose at the repo root uses different credentials — match `.env`):

```bash
docker run --name recipe-db \
  -e POSTGRES_USER=recipe_user \
  -e POSTGRES_PASSWORD=recipe_pass \
  -e POSTGRES_DB=recipe_db \
  -p 5432:5432 -d postgres:16
```

**2. Environment**

```bash
cp .env.example .env
```

Set `TELEGRAM_BOT_TOKEN` and `DATABASE_URL`.

**3. Dependencies**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**4. Migrations**

```bash
alembic upgrade head
```

**5. Server**

```bash
uvicorn app.main:app --reload
```

API: [http://localhost:8000](http://localhost:8000)

### Check auth without Telegram

```bash
python3 scripts/generate_test_init_data.py
```

Run the printed `curl` against `/auth/me`. A tampered hash should return `401`.

## Environment variables

| Variable | Role |
| --- | --- |
| `DATABASE_URL` | SQLAlchemy URL (`postgresql+asyncpg://…`) |
| `TELEGRAM_BOT_TOKEN` | Bot token for HMAC |
| `APP_SECRET_KEY` | App secret |
| `ENVIRONMENT` | e.g. `development` |
| `UPLOAD_DIR` | Photo directory (default `./uploads`) |
