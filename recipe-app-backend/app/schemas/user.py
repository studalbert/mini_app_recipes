from pydantic import BaseModel, ConfigDict


class UserOut(BaseModel):
    # from_attributes=True — позволяет строить схему прямо из SQLAlchemy-объекта
    model_config = ConfigDict(from_attributes=True)

    id: int
    telegram_id: int
    username: str | None
    first_name: str | None
    photo_url: str | None
