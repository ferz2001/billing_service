import json
from datetime import timedelta
from typing import Union

from redis.asyncio import Redis
from core.config import settings
from db.base import AsyncCacheService

redis: Union[None, Redis] = None


async def get_redis() -> Union[Redis, None]:
    return redis


class RedisService(AsyncCacheService):
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def add_token(
            self,
            user_id: str,
            access_token: str,
            user_agent: str,
    ) -> None:
        redis_user = await self.redis.get(user_id)
        values = json.loads(redis_user) if redis_user else {}
        values[user_agent] = access_token

        await self.redis.set(
            name=user_id,
            value=json.dumps(values),
            ex=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_IN),
        )

    async def get(self, name: str) -> dict:
        return json.loads(await self.redis.get(str(name)))

    async def set(self, name: str, value: str):
        await self.redis.set(name=name, value=value)

    async def delete(self, user_id: str):
        await self.redis.delete(user_id)
