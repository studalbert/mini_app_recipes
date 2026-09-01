from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.security import validate_init_data


async def get_current_user(
    authorization: str = Header(..., description="Формат: 'tma <initData>'"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency для защищённых эндпоинтов.

    Ожидает заголовок:
        Authorization: tma <initData строка от Telegram.WebApp.initData>

    Схема "tma" (Telegram Mini App) — рекомендованная Telegram конвенция для
    передачи initData в Authorization-заголовке.

    Проверяет подпись, и если пользователь уже есть в БД — обновляет его
    username/first_name/photo_url (вдруг поменял в Telegram), если нет — создаёт.
    """
    if not authorization.startswith("tma "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный формат заголовка Authorization, ожидается 'tma <initData>'",
        )

    init_data_raw = authorization.removeprefix("tma ")
    parsed = validate_init_data(init_data_raw)

    tg_user = parsed.get("user")
    if not tg_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="В initData нет данных пользователя")

    telegram_id = tg_user["id"]

    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            telegram_id=telegram_id,
            username=tg_user.get("username"),
            first_name=tg_user.get("first_name"),
            photo_url=tg_user.get("photo_url"),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        user.username = tg_user.get("username")
        user.first_name = tg_user.get("first_name")
        user.photo_url = tg_user.get("photo_url")
        await db.commit()

    return user
