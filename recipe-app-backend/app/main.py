from fastapi import FastAPI
from app.routers import auth

app = FastAPI(title="Recipe Mini App API")
app.include_router(auth.router)


@app.get("/health")
async def health_check():
    """Проверка, что сервер жив. Полезно для деплоя/мониторинга."""
    return {"status": "ok"}
