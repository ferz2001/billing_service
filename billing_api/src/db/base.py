import abc
from typing import Union


class AsyncDbServiceBase(abc.ABC):
    @abc.abstractmethod
    async def select(
            self,
            what_select,
            where_select: Union[list, None] = None,
            order_select=None,
            join_with=None,
    ):
        pass

    @abc.abstractmethod
    async def update(
            self,
            what_update,
            values_update: dict,
            where_update: Union[list, None] = None,
    ):
        pass

    @abc.abstractmethod
    async def insert(
            self,
            what_insert,
            values_insert: dict,
    ):
        pass

    @abc.abstractmethod
    async def delete(
            self,
            what_delete,
            where_delete: Union[list, None] = None,
    ):
        pass
