from typing import Union

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, \
    async_sessionmaker
from sqlalchemy.sql import select, update, delete
from core.config import settings
from db.base import AsyncDbServiceBase
from models.base import Base

dsn = (f'postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@'
       f'{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}')
engine = create_async_engine(dsn, echo=settings.db_echo, future=True)

async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


class DbService(AsyncDbServiceBase):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    @staticmethod
    def _prepare_select_sql_query(
            what_select,
            where_select=None,
            order_select=None,
            join_with=None,
    ):
        default_sql = select(what_select)
        if where_select:
            for select_item in where_select:
                default_sql = default_sql.where(
                    select_item[0] == select_item[1],
                )
        if order_select:
            default_sql = default_sql.order_by(order_select())
        if join_with:
            default_sql = default_sql.join(join_with)
        return default_sql

    @staticmethod
    def _prepare_update_sql_query(
            what_update: Base,
            values_update: dict,
            where_update: Union[list, None] = None,
    ):
        default_sql = update(what_update)
        if where_update:
            default_sql = default_sql.where(
                where_update[0] == where_update[1],
            )
        return default_sql.values(**values_update)

    @staticmethod
    def _prepare_delete_sql_query(
            what_delete: Base,
            where_delete=None,
    ):
        default_sql = delete(what_delete)
        if where_delete:
            for select_item in where_delete:
                default_sql = default_sql.where(
                    select_item[0] == select_item[1],
                )
        return default_sql

    async def insert_data(self, data) -> None:
        self.db.add(data)
        await self.db.commit()
        await self.db.refresh(data)

    async def select(
            self,
            what_select: Base,
            where_select=None,
            order_select=None,
            join_with=None,
    ):
        sql = self._prepare_select_sql_query(
            what_select=what_select,
            where_select=where_select,
            order_select=order_select,
            join_with=join_with,
        )
        data = await self.db.execute(sql)
        return list(data.scalars())

    async def update(
            self,
            what_update: Base,
            values_update: dict,
            where_update=None,
    ):
        sql = self._prepare_update_sql_query(
            what_update=what_update,
            values_update=values_update,
            where_update=where_update,
        )
        await self.db.execute(sql)
        await self.db.commit()

    async def insert(
            self,
            what_insert: Base,
            values_insert: dict,
    ):
        new_object = what_insert(**values_insert)
        self.db.add(new_object)
        await self.db.commit()
        return new_object

    async def delete(
            self,
            what_delete: Base,
            where_delete=None,
    ):
        sql = self._prepare_delete_sql_query(
            what_delete=what_delete,
            where_delete=where_delete,
        )
        await self.db.execute(sql)
        await self.db.commit()
