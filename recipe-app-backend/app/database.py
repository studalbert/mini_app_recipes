from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# echo=True полезно на этапе разработки — видно все SQL-запросы в консоли.
# Перед продакшеном лучше поставить False.
engine = create_async_engine(settings.database_url, echo=(settings.environment == "development"))

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для FastAPI: выдаёт сессию БД на время запроса
    и гарантированно закрывает её после.
    Использование в роуте: db: AsyncSession = Depends(get_db)
    """
    async with async_session_maker() as session:
        yield session
