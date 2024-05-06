from abc import abstractmethod, ABC


class AsyncSearchStorage(ABC):
    @abstractmethod
    async def get_by_id(self, **kwargs):
        pass

    @abstractmethod
    async def get_by_query(self, **kwargs):
        pass
