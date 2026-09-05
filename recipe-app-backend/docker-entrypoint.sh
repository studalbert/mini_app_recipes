#!/bin/sh
set -e

echo "Применяю миграции Alembic..."
alembic upgrade head

echo "Запускаю сервер..."
exec gunicorn app.main:app \
    --workers 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
