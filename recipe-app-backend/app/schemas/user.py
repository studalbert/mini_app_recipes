from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    telegram_id: int
    username: str | None
    first_name: str | None
    photo_url: str | None
    created_at: datetime


class ProfileOut(BaseModel):
    """Шапка экрана профиля: данные Telegram + счётчики вкладок."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    telegram_id: int
    username: str | None
    first_name: str | None
    photo_url: str | None
    created_at: datetime
    recipes_count: int
    saved_count: int