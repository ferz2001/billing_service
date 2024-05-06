import os
from typing import Union

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_NAME: str = os.getenv("POSTGRES_DB", "movies_db")
    DB_USER: str = os.getenv("POSTGRES_USER", "auth")
    DB_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "123qwe")
    DB_HOST: str = os.getenv("POSTGRES_HOST", "movies_db")
    DB_PORT: Union[str, int] = os.getenv("POSTGRES_PORT", 4321)
    DB_OPTIONS: str = '-c search_path=content'
    ES_URL: str = os.getenv("ES_URL", "http://elastic:9200")
    POLING_DATA_INTERVAL: int = 5
