from functools import lru_cache

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Business Template"
    PROJECT_VERSION: str = "0.1.0"

    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    AUTH_SECRET_KEY: str = "change-me-in-production"
    AUTH_ALGORITHM: str = "HS256"

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
