from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Все настройки приложения читаются из переменных окружения (.env).
    Смотри .env.example — скопируй его в .env и заполни своими значениями.
    """

    database_url: str
    telegram_bot_token: str
    app_secret_key: str
    environment: str = "development"
    upload_dir: str = "./uploads"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Синглтон настроек — импортируем его везде, где нужны конфиги
settings = Settings()
