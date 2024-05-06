from abc import ABC
import logging
from functools import lru_cache
from typing import Union
from fastapi import Depends

# from core.config import cfg
from db.async_cache_storage import AsyncCacheStorage
from db.async_search_storage import AsyncSearchStorage
from db.elastic import get_elastic_service
from db.redis import get_redis_service
from models.film import Film, Genre, Person


logger = logging.getLogger('movies_api')

class BaseService(ABC):
    pass


class FilmService(BaseService):
    def __init__(self, cache_service: AsyncCacheStorage, search_service: AsyncSearchStorage):
        self.cache_service = cache_service
        self.search_service = search_service

    @staticmethod
    def transform_obj_data_to_data(obj_data: list, elastic_index_name: str) -> list[Union[Film, Genre, Person]]:
        data = []
        elastic_idx_model_ratio = {
            "movies": Film,
            "genres": Genre,
            "persons": Person,
        }
        for obj in obj_data:
            data.append(elastic_idx_model_ratio[elastic_index_name](**obj))
        return data

    async def get_obj_data_by_id(
            self, elastic_index_name: str, obj_id: str,
    ) -> Union[Film, Genre, Person, None]:
        logger.debug('Searching for %d in %s index', obj_id, elastic_index_name)

        redis_structure_key = elastic_index_name + "_" + str(obj_id)
        obj_data = await self.cache_service.get(redis_structure_key)
        if not obj_data:
            obj_data = await self.search_service.get_by_id(obj_id=obj_id, index_name=elastic_index_name)
            if not obj_data:
                return None

            await self.cache_service.set(obj_data, redis_structure_key)

        objects = self.transform_obj_data_to_data(obj_data, elastic_index_name)
        return objects[0]

    async def get_obj_data_by_query(
            self, elastic_index_name: str, query: str, page_size: int, page_number: int,
    ) -> list[Union[Film, Genre, Person, None]]:
        logger.debug('Searching for %s in %s index', query, elastic_index_name)

        redis_structure_key = elastic_index_name + "_" + str(page_size) + "_" + str(page_number) + "_" + str(query)
        obj_data = await self.cache_service.get(redis_structure_key)

        if not obj_data:
            body = {
                'size': page_size,
                'from': (page_number - 1) * page_size,
                'query': {
                    'simple_query_string': {
                        "query": query,
                        "fields": ["title", "description", "name", "full_name"],
                        "default_operator": "or",
                    },
                },
            }
            logger.debug('No item in the cache, searching in elasticsearch')

            obj_data = await self.search_service.get_by_query(
                body=body, index_name=elastic_index_name,
            )
            if not obj_data:
                logger.debug('No item in elasticsearch %s in %s index', query, elastic_index_name)
                return []

            await self.cache_service.set(obj_data, redis_structure_key)
            logger.debug('Save item to the cache %s key', redis_structure_key)

        obj = self.transform_obj_data_to_data(obj_data, elastic_index_name)
        return obj


@lru_cache()
def get_redis_elastic_service(
        redis: AsyncCacheStorage = Depends(get_redis_service),
        elastic_service: AsyncSearchStorage = Depends(get_elastic_service)) -> BaseService:
    return FilmService(redis, elastic_service)
