import os

import pytest
from pydantic_settings import BaseSettings

pytestmark = pytest.mark.asyncio


class Settings(BaseSettings):
    app_host: str = os.getenv("APP_HOST", "127.0.0.1")
    app_port: int = int(os.getenv("APP_PORT", 8000))
    app_api_host: str = f'http://{app_host}:{app_port}/api/v1/'

    redis_host: str = os.getenv("REDIS_HOST", "127.0.0.1")
    redis_port: int = int(os.getenv("REDIS_PORT", 6379))
    redis_db_test: int = int(os.getenv("REDIS_DB_TEST", 6))

    postgres_user: str
    postgres_password: str
    postgres_host: str = "127.0.0.1"
    postgres_port: int = 5432
    postgres_db: str = 'auth_db'

    @property
    def dsl_database(self) -> str:
        return (f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
                f"?async_fallback=True")

    class Config:
        env_prefix = 'AUTH_API_'


settings = Settings()
