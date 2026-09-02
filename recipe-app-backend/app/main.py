from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import auth, recipes
from app.storage import uploads_root

app = FastAPI(title="Recipe Mini App API")

app.include_router(auth.router)
app.include_router(recipes.router)

app.mount("/uploads", StaticFiles(directory=str(uploads_root())), name="uploads")


@app.get("/health")
async def health_check():
    return {"status": "ok"}