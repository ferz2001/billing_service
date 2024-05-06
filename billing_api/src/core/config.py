import os

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = 'billing_api'
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_level: str = 'INFO'

    postgres_user: str = Field(alias='BILLING_API_POSTGRES_USER')
    postgres_password: str = Field(alias='BILLING_API_POSTGRES_PASSWORD')
    postgres_host: str = Field(alias='BILLING_API_POSTGRES_HOST')
    postgres_port: int = Field(alias='BILLING_API_POSTGRES_PORT')
    postgres_db: str = Field(alias='BILLING_API_POSTGRES_DB')
    db_echo: bool = True
    redis_host: str = Field(alias='AUTH_API_REDIS_HOST')
    redis_port: int = Field(alias='AUTH_API_REDIS_PORT')
    jwt_secret_key: str = Field(alias='AUTH_API_JWT_SECRET_KEY')
    jwt_algorithm: str = Field(alias='AUTH_API_JWT_ALGORITHM')
    yookassa_shop_id: str = Field(alias='YOOKASSA_SHOP_ID')
    yookassa_secret_key: str = Field(alias='YOOKASSA_SECRET_KEY')
    return_url: str = '127.0.0.1'
    auth_api_login_url: str = 'http://auth_api:8000/api/v1/auth/signin/'

    @property
    def dsl_database(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            f"?async_fallback=True")

    class Config:
        env_prefix = 'BILLING_API_'


settings = Settings()
