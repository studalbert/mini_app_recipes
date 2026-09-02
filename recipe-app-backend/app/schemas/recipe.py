from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class RecipeImageOut(BaseModel):
    id: int
    url: str
    position: int


class IngredientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    position: int


class RecipeCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    cooking_process: str = Field(min_length=1, description="Текст с описанием процесса готовки")
    is_public: bool = Field(default=True, description="False — рецепт не попадёт в общую ленту")
    ingredients: list[str] = Field(
        default_factory=list, description="Список ингредиентов, один элемент — одно текстовое поле"
    )


class RecipeUpdate(BaseModel):
    """Все поля опциональны — обновляется только то, что реально передано в запросе."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    cooking_process: str | None = Field(default=None, min_length=1)
    is_public: bool | None = None
    ingredients: list[str] | None = Field(
        default=None, description="Если передано — полностью заменяет старый список ингредиентов"
    )


class RecipeOut(BaseModel):
    """Полная версия рецепта — для страницы одного рецепта."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    author_id: int
    title: str
    cooking_process: str
    is_public: bool
    created_at: datetime
    updated_at: datetime
    ingredients: list[IngredientOut]
    images: list[RecipeImageOut] = []


class RecipeListItem(BaseModel):
    """Облегчённая версия для списков — без текста готовки и ингредиентов."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    author_id: int
    title: str
    is_public: bool
    created_at: datetime
    cover_url: str | None = None
