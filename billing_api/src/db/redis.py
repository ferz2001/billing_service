import json
from typing import Union

from redis.asyncio import Redis

redis: Union[None, Redis] = None


async def get_redis() -> Union[None, Redis]:
    return redis


class RedisService:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def get(self, name: str) -> dict:
        return json.loads(await self.redis.get(str(name)))
