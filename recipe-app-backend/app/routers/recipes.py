from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Ingredient, Recipe, RecipeImage, User
from app.schemas.recipe import RecipeCreate, RecipeImageOut, RecipeListItem, RecipeOut, RecipeUpdate
from app.storage import (
    MAX_IMAGES_PER_RECIPE,
    delete_file,
    delete_recipe_dir,
    public_url,
    read_image_bytes,
    save_recipe_image,
)

router = APIRouter(prefix="/recipes", tags=["recipes"])

_RECIPE_LOAD = (selectinload(Recipe.ingredients), selectinload(Recipe.images))


def _image_out(image: RecipeImage) -> RecipeImageOut:
    return RecipeImageOut(id=image.id, url=public_url(image.file_path), position=image.position)


def _recipe_out(recipe: Recipe) -> RecipeOut:
    return RecipeOut(
        id=recipe.id,
        author_id=recipe.author_id,
        title=recipe.title,
        cooking_process=recipe.cooking_process,
        is_public=recipe.is_public,
        created_at=recipe.created_at,
        updated_at=recipe.updated_at,
        ingredients=recipe.ingredients,
        images=[_image_out(img) for img in recipe.images],
    )


def _list_item(recipe: Recipe) -> RecipeListItem:
    cover = recipe.images[0] if recipe.images else None
    return RecipeListItem(
        id=recipe.id,
        author_id=recipe.author_id,
        title=recipe.title,
        is_public=recipe.is_public,
        created_at=recipe.created_at,
        cover_url=public_url(cover.file_path) if cover else None,
    )


async def _get_owned_recipe(recipe_id: int, current_user: User, db: AsyncSession) -> Recipe:
    result = await db.execute(
        select(Recipe).options(*_RECIPE_LOAD).where(Recipe.id == recipe_id)
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
    await db.refresh(recipe, attribute_names=["ingredients", "images"])
    return _recipe_out(recipe)


@router.get("", response_model=list[RecipeListItem])
async def list_public_recipes(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Recipe)
        .options(selectinload(Recipe.images))
        .where(Recipe.is_public.is_(True))
        .order_by(Recipe.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return [_list_item(r) for r in result.scalars().all()]


@router.get("/my", response_model=list[RecipeListItem])
async def list_my_recipes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Recipe)
        .options(selectinload(Recipe.images))
        .where(Recipe.author_id == current_user.id)
        .order_by(Recipe.created_at.desc())
    )
    return [_list_item(r) for r in result.scalars().all()]


@router.get("/{recipe_id}", response_model=RecipeOut)
async def get_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Recipe).options(*_RECIPE_LOAD).where(Recipe.id == recipe_id)
    )
    recipe = result.scalar_one_or_none()
    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Рецепт не найден")
    return _recipe_out(recipe)


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
        recipe.ingredients = [
            Ingredient(text=text, position=i) for i, text in enumerate(payload.ingredients)
        ]

    await db.commit()
    await db.refresh(recipe, attribute_names=["ingredients", "images"])
    return _recipe_out(recipe)


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    recipe = await _get_owned_recipe(recipe_id, current_user, db)
    await db.delete(recipe)
    await db.commit()
    delete_recipe_dir(recipe_id)


@router.post("/{recipe_id}/images", response_model=list[RecipeImageOut], status_code=status.HTTP_201_CREATED)
async def upload_recipe_images(
    recipe_id: int,
    files: list[UploadFile] = File(..., description="Одно или несколько фото"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    recipe = await _get_owned_recipe(recipe_id, current_user, db)

    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нет файлов")

    remaining = MAX_IMAGES_PER_RECIPE - len(recipe.images)
    if remaining <= 0 or len(files) > remaining:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Максимум {MAX_IMAGES_PER_RECIPE} фото на рецепт",
        )

    payloads: list[bytes] = []
    for upload in files:
        payloads.append(await read_image_bytes(upload))

    next_position = (max((img.position for img in recipe.images), default=-1) + 1)
    created: list[RecipeImage] = []
    saved_paths: list[str] = []

    try:
        for i, data in enumerate(payloads):
            relative = save_recipe_image(recipe.id, data)
            saved_paths.append(relative)
            image = RecipeImage(recipe_id=recipe.id, file_path=relative, position=next_position + i)
            db.add(image)
            created.append(image)
        await db.commit()
        for image in created:
            await db.refresh(image)
    except Exception:
        for path in saved_paths:
            delete_file(path)
        raise

    return [_image_out(image) for image in created]


@router.delete("/{recipe_id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe_image(
    recipe_id: int,
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    recipe = await _get_owned_recipe(recipe_id, current_user, db)
    image = next((img for img in recipe.images if img.id == image_id), None)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Фото не найдено")

    file_path = image.file_path
    await db.delete(image)
    await db.commit()
    delete_file(file_path)