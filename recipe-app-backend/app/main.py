from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import auth, profile, recipes
from app.storage import uploads_root

app = FastAPI(title="Recipe Mini App API")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(recipes.router)

app.mount("/uploads", StaticFiles(directory=str(uploads_root())), name="uploads")


@app.get("/health")
async def health_check():
    return {"status": "ok"}