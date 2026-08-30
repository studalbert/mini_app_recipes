from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    # telegram_id приходит из initData — используем BigInteger,
    # т.к. Telegram ID пользователей может быть больше int32
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)

    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Рецепты, которые пользователь создал
    recipes: Mapped[list["Recipe"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )

    # Рецепты, которые пользователь сохранил себе (избранное)
    saved_recipes: Mapped[list["SavedRecipe"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
