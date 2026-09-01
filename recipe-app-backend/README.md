# Recipe Mini App — Backend (шаг 3 из плана)

## Что уже сделано
- Структура проекта FastAPI
- SQLAlchemy 2.0 (async) модели: `User`, `Recipe`, `RecipeImage`, `Ingredient`, `SavedRecipe`
- Настроен Alembic для миграций (async-совместимый `env.py`)
- Базовый `main.py` с `/health`
- **Авторизация через Telegram `initData`** (`app/security.py`, `app/dependencies.py`)
- Эндпоинт `GET /auth/me` — проверка подписи + автосоздание пользователя
- Скрипт `scripts/generate_test_init_data.py` для локального тестирования без Telegram

## Как проверить авторизацию локально

1. В `.env` укажи `TELEGRAM_BOT_TOKEN` — реальный токен твоего бота
   (получить у [@BotFather](https://t.me/BotFather), команда `/newbot` или `/mybots` → `API Token`).

2. Запусти сервер:
   ```bash
   uvicorn app.main:app --reload
   ```

3. Сгенерируй тестовую initData:
   ```bash
   python3 scripts/generate_test_init_data.py
   ```

4. Скопируй curl-команду из вывода скрипта и выполни её. Если всё настроено
   верно — увидишь JSON с данными пользователя (и он появится в таблице `users`).

5. Попробуй с неверным/битым hash — должен вернуться `401 Unauthorized`.

## Как это будет работать в реальном Mini App

На фронтенде (шаг 8) вместо скрипта используется настоящая `initData`:
```js
const initData = window.Telegram.WebApp.initData;
fetch('/auth/me', {
  headers: { Authorization: `tma ${initData}` }
});
```
Каждый защищённый запрос к API должен нести этот заголовок — отдельного JWT
или сессии не заводим, initData от Telegram сама по себе служит подтверждением.

## Как запустить локально

1. Установи PostgreSQL локально (или подними в Docker):
   ```bash
   docker run --name recipe-db -e POSTGRES_USER=recipe_user \
     -e POSTGRES_PASSWORD=recipe_pass -e POSTGRES_DB=recipe_db \
     -p 5432:5432 -d postgres:16
   ```

2. Скопируй `.env.example` в `.env` и подставь свои значения:
   ```bash
   cp .env.example .env
   ```

3. Создай виртуальное окружение и поставь зависимости:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Сгенерируй и примени первую миграцию:
   ```bash
   alembic revision --autogenerate -m "init tables"
   alembic upgrade head
   ```

5. Запусти сервер:
   ```bash
   uvicorn app.main:app --reload
   ```

6. Открой http://localhost:8000/docs — увидишь Swagger UI со списком эндпоинтов
   (пока там только `/health`).

## Структура проекта

```
recipe-app-backend/
├── app/
│   ├── main.py          # точка входа FastAPI
│   ├── config.py        # настройки из .env
│   ├── database.py      # подключение к БД, Base, get_db()
│   ├── security.py      # проверка подписи Telegram initData
│   ├── dependencies.py  # get_current_user — auth-зависимость для роутов
│   ├── models/          # SQLAlchemy модели
│   │   ├── user.py
│   │   ├── recipe.py
│   │   ├── recipe_image.py
│   │   ├── ingredient.py
│   │   └── saved_recipe.py
│   ├── schemas/         # Pydantic-схемы для API
│   │   └── user.py
│   └── routers/         # эндпоинты, сгруппированные по темам
│       └── auth.py
├── scripts/
│   └── generate_test_init_data.py  # генератор тестовой initData
├── alembic/             # миграции БД
├── requirements.txt
└── .env.example
```

## Что дальше (следующие шаги)
4. CRUD рецептов (создание/редактирование/удаление, приватность)
5. Загрузка и хранение фотографий
6. Избранное ("добавленные к себе рецепты")
7. Эндпоинты профиля пользователя
8. Фронтенд на React + Telegram WebApp SDK
9. Деплой