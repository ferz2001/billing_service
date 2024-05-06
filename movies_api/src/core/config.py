import os
from typing import Union

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = "Some project name"
    redis_host: str = '127.0.0.1'
    auth_url: str = ''
    redis_port: Union[str, int] = 6379
    elastic_host: str = 'elastic'
    elastic_port: Union[str, int] = 9200
    base_dir: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_level: str = 'INFO'

    app_name: str = 'movies_api'

    class Config:
        env_prefix = 'MOVIES_API_'


cfg = Settings()
