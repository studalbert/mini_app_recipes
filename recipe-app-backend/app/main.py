from fastapi import FastAPI

app = FastAPI(title="Recipe Mini App API")


@app.get("/health")
async def health_check():
    """Проверка, что сервер жив. Полезно для деплоя/мониторинга."""
    return {"status": "ok"}
