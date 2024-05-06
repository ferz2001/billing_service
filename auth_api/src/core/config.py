from pydantic_settings import BaseSettings


class OauthSettings(BaseSettings):
    yandex_client_id: str
    yandex_client_secret: str

    vk_client_id: str
    vk_client_secret: str
    vk_redirect_uri: str

    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str
    google_scope: str = 'https://www.googleapis.com/auth/userinfo.email'

    class Config:
        env_prefix = 'AUTH_API_'


class Settings(BaseSettings):
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    session_secret_key: str

    redis_host: str = "127.0.0.1"
    redis_port: int = 6379

    enable_tracer: bool = True
    jaeger_agent_host: str = "127.0.0.1"
    jaeger_agent_port: int = 6831

    enable_rate_limiter: bool = False
    rate_limiter_times: int = 2
    rate_limiter_seconds: int = 5

    postgres_user: str
    postgres_password: str
    postgres_host: str = "127.0.0.1"
    postgres_port: int = 5432
    postgres_db: str = 'auth_db'
    db_echo: bool = False

    JWT_SECRET_KEY: str
    REFRESH_TOKEN_EXPIRES_IN: int = 60
    ACCESS_TOKEN_EXPIRES_IN: int = 10
    JWT_ALGORITHM: str = 'HS256'

    @property
    def dsl_database(self) -> str:
        return (f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
                f"?async_fallback=True")
    
    app_name: str = 'auth_api'
    log_level: str = 'INFO'
    sentry_dsn: str | None = None

    class Config:
        env_prefix = 'AUTH_API_'


oauth_settings = OauthSettings()
settings = Settings()
