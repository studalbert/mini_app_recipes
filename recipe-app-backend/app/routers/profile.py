from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Recipe, SavedRecipe, User
from app.schemas.user import ProfileOut

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ProfileOut)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    recipes_count = await db.scalar(
        select(func.count()).select_from(Recipe).where(Recipe.author_id == current_user.id)
    )
    saved_count = await db.scalar(
        select(func.count()).select_from(SavedRecipe).where(SavedRecipe.user_id == current_user.id)
    )

    return ProfileOut(
        id=current_user.id,
        telegram_id=current_user.telegram_id,
        username=current_user.username,
        first_name=current_user.first_name,
        photo_url=current_user.photo_url,
        created_at=current_user.created_at,
        recipes_count=recipes_count or 0,
        saved_count=saved_count or 0,
    )