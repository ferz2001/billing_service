import uvicorn
from contextlib import asynccontextmanager
import logging
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis
import asgi_correlation_id
from api.v1 import films, genres, persons
from core.config import cfg
from core.logger import LoggerSetup
from db import redis, elastic
from db.elastic import ElasticService
from db.redis import RedisService

logging_setup = LoggerSetup()
logger = logging.getLogger('movies_api')


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis_service = RedisService(Redis(host=cfg.redis_host, port=cfg.redis_port))
    elastic.elastic_service = ElasticService(AsyncElasticsearch(hosts=[f'{cfg.elastic_host}:{cfg.elastic_port}']))
    logger.info('Movies API service started')
    yield
    await redis.redis_service.redis.close()
    await elastic.elastic_service.elastic.close()


app = FastAPI(
    lifespan=lifespan,
    title=cfg.project_name,
    docs_url='/api/v1/movies/openapi',
    openapi_url='/api/v1/movies/openapi.json',
    default_response_class=ORJSONResponse,
)

app.include_router(films.router, prefix='/api/v1/movies/films', tags=['films'])
app.include_router(genres.router, prefix='/api/v1/movies/genres', tags=['genres'])
app.include_router(persons.router, prefix='/api/v1/movies/persons', tags=['persons'])

app.add_middleware(asgi_correlation_id.CorrelationIdMiddleware)


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        reload=True,
    )
