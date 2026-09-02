import shutil
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.config import settings

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 МБ
MAX_IMAGES_PER_RECIPE = 10
READ_CHUNK = 64 * 1024


def uploads_root() -> Path:
    root = Path(settings.upload_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def public_url(file_path: str) -> str:
    """Относительный путь из БД → URL, который отдаёт StaticFiles."""
    return f"/uploads/{file_path.lstrip('/')}"


def detect_extension(data: bytes) -> str:
    """Определяем тип по сигнатуре файла, а не по Content-Type/имени."""
    if data.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Допустимы только jpeg, png и webp",
    )


async def read_image_bytes(upload: UploadFile) -> bytes:
    chunks: list[bytes] = []
    size = 0
    while True:
        chunk = await upload.read(READ_CHUNK)
        if not chunk:
            break
        size += len(chunk)
        if size > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Файл больше 5 МБ",
            )
        chunks.append(chunk)

    if size == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пустой файл")

    return b"".join(chunks)


def save_recipe_image(recipe_id: int, data: bytes) -> str:
    """Пишет файл на диск, возвращает относительный путь для БД."""
    ext = detect_extension(data)
    relative = Path("recipes") / str(recipe_id) / f"{uuid.uuid4().hex}.{ext}"
    absolute = uploads_root() / relative
    absolute.parent.mkdir(parents=True, exist_ok=True)
    absolute.write_bytes(data)
    return relative.as_posix()


def delete_file(file_path: str) -> None:
    absolute = uploads_root() / file_path
    try:
        absolute.unlink(missing_ok=True)
    except OSError:
        pass


def delete_recipe_dir(recipe_id: int) -> None:
    folder = uploads_root() / "recipes" / str(recipe_id)
    shutil.rmtree(folder, ignore_errors=True)