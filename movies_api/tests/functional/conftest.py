import aiohttp
import aioredis
import pytest
from elasticsearch import AsyncElasticsearch

from settings import cfg


@pytest.fixture(scope='function')
async def es_client():
    client = AsyncElasticsearch(hosts=cfg.es_host)
    yield client
    await client.close()


@pytest.fixture(scope='function')
async def redis_conn():
    redis = await aioredis.from_url(f"redis://{cfg.redis_host}:{cfg.redis_port}")
    yield redis
    await redis.close()


@pytest.fixture(scope='function')
async def session():
    async with aiohttp.ClientSession() as session:
        yield session
    await session.close()
