import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl

from fastapi import HTTPException, status

from app.config import settings

# Считаем initData устаревшей через сутки — защита от replay-атак
# (повторного использования перехваченной когда-то строки initData)
INIT_DATA_MAX_AGE_SECONDS = 24 * 60 * 60


def validate_init_data(init_data: str) -> dict:
    """
    Проверяет подпись Telegram WebApp initData и возвращает распарсенные данные.

    Алгоритм проверки (официальный, из документации Telegram):
    https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app

    1. Забираем hash из данных, остальные пары сортируем по ключу и склеиваем в
       строку вида "key=value\nkey2=value2..." — это data_check_string.
    2. secret_key = HMAC_SHA256(key="WebAppData", data=bot_token)
    3. Считаем HMAC_SHA256(key=secret_key, data=data_check_string) — если совпадает
       с присланным hash, значит данные пришли от Telegram и не были подделаны.
    """
    try:
        # strict_parsing=True — чтобы явно упасть на кривом формате, а не тихо потерять часть данных
        parsed = dict(parse_qsl(init_data, strict_parsing=True))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Некорректный формат initData")

    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Отсутствует hash в initData")

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))

    secret_key = hmac.new(b"WebAppData", settings.telegram_bot_token.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    # compare_digest вместо == — защита от timing-атак при сравнении хэшей
    if not hmac.compare_digest(computed_hash, received_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверная подпись initData")

    auth_date = int(parsed.get("auth_date", 0))
    if time.time() - auth_date > INIT_DATA_MAX_AGE_SECONDS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="initData устарела, перезапусти Mini App")

    # Поле "user" в initData приходит как JSON-строка — разбираем в dict
    if "user" in parsed:
        parsed["user"] = json.loads(parsed["user"])

    return parsed
