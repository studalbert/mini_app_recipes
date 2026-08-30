from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RecipeImage(Base):
    __tablename__ = "recipe_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), index=True)

    # Храним не сам файл, а путь/URL до него (файл лежит в хранилище — диск или S3)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)

    # Порядок отображения, если фото несколько
    position: Mapped[int] = mapped_column(Integer, default=0)

    recipe: Mapped["Recipe"] = relationship(back_populates="images")
