from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Ingredient, Recipe, User
from app.schemas.recipe import RecipeCreate, RecipeListItem, RecipeOut, RecipeUpdate

router = APIRouter(prefix="/recipes", tags=["recipes"])


async def _get_owned_recipe(recipe_id: int, current_user: User, db: AsyncSession) -> Recipe:
    """Достаёт рецепт и проверяет, что текущий пользователь — его автор. Иначе 404/403."""
    result = await db.execute(
        select(Recipe).options(selectinload(Recipe.ingredients)).where(Recipe.id == recipe_id)
    )
    recipe = result.scalar_one_or_none()
    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Рецепт не найден")
    if recipe.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Это не твой рецепт")
    return recipe


@router.post("", response_model=RecipeOut, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    payload: RecipeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    recipe = Recipe(
        author_id=current_user.id,
        title=payload.title,
        cooking_process=payload.cooking_process,
        is_public=payload.is_public,
        ingredients=[Ingredient(text=text, position=i) for i, text in enumerate(payload.ingredients)],
    )

    db.add(recipe)
    await db.commit()
    await db.refresh(recipe, attribute_names=["ingredients"])
    return recipe


@router.get("", response_model=list[RecipeListItem])
async def list_public_recipes(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """Общая лента — только публичные рецепты, от всех авторов, свежие сверху."""
    result = await db.execute(
        select(Recipe)
        .where(Recipe.is_public.is_(True))
        .order_by(Recipe.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


@router.get("/my", response_model=list[RecipeListItem])
async def list_my_recipes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Вкладка профиля "мои рецепты" — и публичные, и приватные, только свои."""
    result = await db.execute(
        select(Recipe).where(Recipe.author_id == current_user.id).order_by(Recipe.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{recipe_id}", response_model=RecipeOut)
async def get_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    """
    Открыт по прямой ссылке для всех, независимо от is_public — как договорились:
    приватность влияет только на попадание в списки (/recipes и /recipes/my),
    а не на доступ по конкретному recipe_id.
    """
    result = await db.execute(
        select(Recipe).options(selectinload(Recipe.ingredients)).where(Recipe.id == recipe_id)
    )
    recipe = result.scalar_one_or_none()
    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Рецепт не найден")
    return recipe


@router.put("/{recipe_id}", response_model=RecipeOut)
async def update_recipe(
    recipe_id: int,
    payload: RecipeUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    recipe = await _get_owned_recipe(recipe_id, current_user, db)

    if payload.title is not None:
        recipe.title = payload.title
    if payload.cooking_process is not None:
        recipe.cooking_process = payload.cooking_process
    if payload.is_public is not None:
        recipe.is_public = payload.is_public
    if payload.ingredients is not None:
        # Полная замена списка проще и надёжнее, чем построчное сравнение старого/нового.
        # cascade="all, delete-orphan" на модели Recipe сам удалит старые Ingredient-записи.
        recipe.ingredients = [
            Ingredient(text=text, position=i) for i, text in enumerate(payload.ingredients)
        ]

    await db.commit()
    await db.refresh(recipe, attribute_names=["ingredients"])
    return recipe


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    recipe = await _get_owned_recipe(recipe_id, current_user, db)
    await db.delete(recipe)
    await db.commit()
