from pydantic import Field
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    app_host: str = Field('http://movies_api_tests:8000', alias='TEST_FASTAPI_HOST')
    es_host: str = Field('127.0.0.1:9200', alias='ELASTIC_HOST')
    redis_host: str = Field('127.0.0.1', alias='REDIS_HOST')
    redis_port: str = Field('6379', alias='REDIS_PORT')


cfg = TestSettings()
