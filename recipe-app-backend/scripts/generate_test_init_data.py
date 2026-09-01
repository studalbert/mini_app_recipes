"""
Генерирует валидную тестовую строку initData, подписанную твоим TELEGRAM_BOT_TOKEN
из .env — точно так же, как это делает настоящий Telegram при открытии Mini App.

Нужно для локальной отладки эндпоинтов авторизации через curl/Postman,
пока нет готового фронтенда.

Запуск (из корня проекта):
    python3 scripts/generate_test_init_data.py

Использование результата:
    curl http://localhost:8000/auth/me \
      -H "Authorization: tma <вставь сюда результат скрипта>"
"""
import hashlib
import hmac
import json
import sys
import time
from pathlib import Path
from urllib.parse import quote, urlencode

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings  # noqa: E402


def build_test_init_data(telegram_id: int = 123456789, username: str = "test_user",
                          first_name: str = "Тест") -> str:
    user_payload = json.dumps(
        {"id": telegram_id, "first_name": first_name, "username": username, "language_code": "ru"},
        ensure_ascii=False,
        separators=(",", ":"),
    )

    fields = {
        "user": user_payload,
        "auth_date": str(int(time.time())),
        "query_id": "AAHtest_query_id",
    }

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(fields.items()))

    secret_key = hmac.new(b"WebAppData", settings.telegram_bot_token.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    fields["hash"] = computed_hash

    # quote_via=quote — чтобы получить корректно urlencoded строку, как присылает сам Telegram
    return urlencode(fields, quote_via=quote)


if __name__ == "__main__":
    init_data = build_test_init_data()
    print("\nТестовая initData (валидна 24 часа):\n")
    print(init_data)
    print("\nПример запроса:\n")
    print(f'curl http://localhost:8000/auth/me -H "Authorization: tma {init_data}"\n')
