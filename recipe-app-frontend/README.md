# Recipe Mini App — Frontend

Telegram Mini App UI for browsing, creating, and saving recipes. Talks to [`recipe-app-backend`](../recipe-app-backend) and uses Telegram WebApp `initData` as the auth token.

Built for a phone-sized WebView (tab bar, haptic feedback, expanded viewport). It also runs in a desktop browser with a generated `initData` string.

## Features

- **Feed** — public recipes, debounced search by title
- **Recipe** — photos, ingredients, cooking steps; save / unsave if it is not yours
- **Editor** — create and edit own recipes, public/private flag, multi-photo upload
- **Profile** — Telegram name and photo, counts, tabs “Mine” / “Saved”
- Auth header `Authorization: tma <initData>` on every API call
- Telegram SDK: `ready`, `expand`, optional haptic feedback

## Tech stack

| Layer | Choice |
| --- | --- |
| UI | React 19 |
| Routing | React Router 7 |
| Build | Vite 8 |
| Telegram | `telegram-web-app.js` |
| Lint | Oxlint |

No extra UI kit: layout and styles are custom CSS aimed at Mini App chrome.

## Screens

```
/                 public feed + search
/recipe/:id       recipe detail
/new              create
/edit/:id         edit (author)
/profile          my recipes / saved
```

Bottom nav: **Feed** · **+** · **Profile**.

## How auth works in the client

Inside Telegram:

```js
window.Telegram.WebApp.initData
```

is sent as `Authorization: tma …`. The backend verifies the HMAC with the bot token.

Outside Telegram (local browser), set `VITE_DEV_INIT_DATA` from the backend script `scripts/generate_test_init_data.py`.

## Project layout

```
recipe-app-frontend/
├── index.html              # Telegram WebApp script
├── vite.config.js
├── src/
│   ├── main.jsx
│   ├── App.jsx             # routes + tab bar
│   ├── api.js              # fetch + auth header
│   ├── telegram.js         # WebApp helpers
│   ├── styles.css
│   ├── components/
│   │   └── RecipeCard.jsx
│   └── screens/
│       ├── Feed.jsx
│       ├── Recipe.jsx
│       ├── Editor.jsx
│       └── Profile.jsx
└── .env.example
```

## Run locally

Needs the API on `VITE_API_URL` (default `http://127.0.0.1:8000`).

**1. Environment**

```bash
cp .env.example .env
```

```env
VITE_API_URL=http://127.0.0.1:8000
VITE_DEV_INIT_DATA=
```

For browser-only testing, paste initData from the backend generator into `VITE_DEV_INIT_DATA`. Restart Vite after changing env files.

**2. Install and start**

```bash
npm install
npm run dev
```

App: [http://localhost:5173](http://localhost:5173)

**3. Other scripts**

```bash
npm run build    # production bundle
npm run preview  # serve the bundle
npm run lint     # oxlint
```

## Telegram Mini App

1. HTTPS frontend + reachable API (or a tunnel in development).
2. Bot: BotFather → Mini App URL = frontend origin.
3. Backend `.env`: same bot’s `TELEGRAM_BOT_TOKEN`.
4. CORS on the API must allow the Mini App origin (dev currently allows `*`).

In Telegram, `initData` is used automatically; `VITE_DEV_INIT_DATA` is ignored when the WebApp object is present.

## Pairing with the API

| Client | Backend |
| --- | --- |
| `GET /recipes?q=` | public feed + search |
| `POST /recipes` + `POST …/images` | create + photos |
| `PUT /recipes/:id` | edit |
| `POST/DELETE /recipes/:id/save` | save / unsave |
| `GET /recipes/my`, `/recipes/saved` | profile tabs |
| `GET /profile` | header stats |
