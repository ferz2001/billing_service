import asyncio
import aioredis

import repackage

repackage.up()

from settings import cfg
from utils.backoff import backoff


@backoff()
async def wait_redis():
    client = await aioredis.from_url(f"redis://{cfg.redis_host}:{cfg.redis_port}")
    response = await client.ping()
    while not response:
        await asyncio.sleep(2)
        response = await client.ping()


if __name__ == '__main__':
    asyncio.run(wait_redis())
