from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from pathlib import Path


class Settings(BaseSettings):
    BOT_TOKEN: str

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    REDIS_HOST: str
    REDIS_PORT: int

    MAIN_MENU_BOT: dict = {
        "/start": "Старт бота и регистрация",
        "/menu": "Главное меню",
        "/help": "Техническая поддержка",
    }

    model_config = ConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
