import asyncio
from elasticsearch import AsyncElasticsearch

import repackage

repackage.up()

from settings import cfg
from utils.backoff import backoff


@backoff()
async def wait_es():
    client = AsyncElasticsearch(hosts=[cfg.es_host])
    response = await client.ping()
    while not response:
        await asyncio.sleep(2)
        response = await client.ping()
    await client.close()


if __name__ == '__main__':
    asyncio.run(wait_es())
