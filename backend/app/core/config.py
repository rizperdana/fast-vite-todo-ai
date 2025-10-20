import os
from typing import Annotated, Any, Literal
from pydantic import AnyUrl, BeforeValidator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv


load_dotenv()


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )
    DEBUG: str | None = os.getenv("DEBUG")

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    SECRET_KEY: str = "21jkh3lkj1h2j2k1h3jh$%#%^$%^&$"
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    DOMAIN: str = "localhost"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    PROJECT_NAME: str = "Boilerplate fast vite"
    GENERATE_SCHEMAS: bool = True

    # Redis
    REDIS_HOST: str | None = os.getenv("REDIS_HOST")
    REDIS_PORT: str | None = os.getenv("REDIS_PORT")
    REDIS_PASSWORD: str | None = os.getenv("REDIS_PASSWORD")
    REDIS_DB: str | None = os.getenv("REDIS_DB")
    REDIS_USE_SSL: str | None = os.getenv("REDIS_USE_SSL")
    RFQ_DUPLICATE_EXPIRY_HOURS: int | None = 24 * 7  # 1 week

    # Postgres
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_USER: str | None = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str | None = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DATABASE: str | None = os.getenv("POSTGRES_DATABASE")
    POSTGRES_PORT: str | None = os.getenv("POSTGRES_PORT")
    POSTGRES_DATABASE_SCHEMA: str | None = None


settings = Settings()
