import asyncio

import asyncpg

from tests.functional.settings import settings
from tests.functional.utils.helpers import backoff


@backoff(start_sleep_time=1, factor=2, border_sleep_time=20)
async def main():
    conn = await asyncpg.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        user=settings.postgres_user,
        password=settings.postgres_password,
        database=settings.postgres_db
    )
    await conn.execute('SELECT 1')


if __name__ == '__main__':
    asyncio.run(main())
