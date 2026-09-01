from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.models import User
from app.schemas.user import UserOut


router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Возвращает данные текущего пользователя на основе initData из заголовка.
    Если пользователь заходит первый раз — создаётся автоматически.
    Используй этот эндпоинт, чтобы проверить, что авторизация работает.
    """
    return current_user
