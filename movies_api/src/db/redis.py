import json
from typing import Union

import backoff
from redis.asyncio import Redis
from db.async_cache_storage import AsyncCacheStorage

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class RedisService(AsyncCacheStorage):
    def __init__(self, redis: Redis):
        self.redis = redis

    @backoff.on_exception(backoff.expo, Exception)
    async def get(self, key: str) -> Union[dict, None]:
        data_bytes = await self.redis.get(key)
        if not data_bytes:
            return None

        dict_data = json.loads(data_bytes.decode('utf-8'))
        return dict_data

    @backoff.on_exception(backoff.expo, Exception)
    async def set(self, obj_data: list, redis_structure_key: str):
        await self.redis.set(redis_structure_key, json.dumps(obj_data), FILM_CACHE_EXPIRE_IN_SECONDS)


redis_service: Union[None, RedisService]


async def get_redis_service() -> Union[RedisService, None]:
    global redis_service
    return redis_service
