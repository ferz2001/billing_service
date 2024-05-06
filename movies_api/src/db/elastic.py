from typing import Union

import backoff
from elasticsearch import AsyncElasticsearch, NotFoundError
from db.async_search_storage import AsyncSearchStorage


class ElasticService(AsyncSearchStorage):
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    @backoff.on_exception(backoff.expo, Exception)
    async def get_by_query(self, index_name: str, body: dict) -> Union[list, None]:
        try:
            doc = await self.elastic.search(index=index_name, body=body)
            obj_data = []
            for obj in doc['hits']['hits']:
                obj_data.append(obj['_source'])
            return obj_data
        except NotFoundError:
            return None

    @backoff.on_exception(backoff.expo, Exception)
    async def get_by_id(self, index_name: str, obj_id: str) -> Union[list, None]:
        try:
            doc = await self.elastic.get(index=index_name, id=obj_id)
            return [doc['_source']]
        except NotFoundError:
            return None


elastic_service: Union[None, ElasticService]


async def get_elastic_service() -> Union[ElasticService, None]:
    global elastic_service
    return elastic_service
