# Recipe Mini App — Backend (шаг 2 из плана)

## Что уже сделано
- Структура проекта FastAPI
- SQLAlchemy 2.0 (async) модели: `User`, `Recipe`, `RecipeImage`, `Ingredient`, `SavedRecipe`
- Настроен Alembic для миграций (async-совместимый `env.py`)
- Базовый `main.py` с `/health`

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
│   └── models/          # SQLAlchemy модели
│       ├── user.py
│       ├── recipe.py
│       ├── recipe_image.py
│       ├── ingredient.py
│       └── saved_recipe.py
├── alembic/             # миграции БД
├── requirements.txt
└── .env.example
```

## Что дальше (следующие шаги)
3. Авторизация через Telegram `initData`
4. CRUD рецептов (создание/редактирование/удаление, приватность)
5. Загрузка и хранение фотографий
6. Избранное ("добавленные к себе рецепты")
7. Эндпоинты профиля пользователя
8. Фронтенд на React + Telegram WebApp SDK
9. Деплой
