from functools import lru_cache
from pydantic import PostgresDsn, computed_field
from pydantic_core import MultiHostUrl
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
    PSQL_DIALECT: str = "postgresql+psycopg"  # +psycopg is necessary for newer psycopg support (vs. default==psycopg2)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return MultiHostUrl.build(
            scheme=self.PSQL_DIALECT,
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            path=self.DB_NAME,
        )

    API_PREFIX: str = "/api/v1"

    # Secret Algorithm Key for JWT Token generation
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(env_file=".env")


# caching to avoid unneeded duplicate fetching of settings values
@lru_cache
def get_settings():
    return Settings()
