from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """These variables should be stored in a `.env` file in the project's base directory"""
    APP_NAME: str = "FastAPI Social Media Demo API"

    # DB values are required for the PostgreSQL database connection
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    API_PREFIX: str = "/api/v1"

    # Secret Algorithm Key for JWT Token generation
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return Settings()
