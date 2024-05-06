import asyncio
import json
from typing import Generator, List, Union

from aiohttp import ClientSession
from elasticsearch import AsyncElasticsearch, exceptions, helpers, NotFoundError

from settings import cfg


async def load_docs(es_client: AsyncElasticsearch, index: str, docs: List[dict]):
    bulk_query = []
    for row in docs:
        bulk_query.extend([
            json.dumps({'index': {'_index': index, '_id': row["id"]}}),
            json.dumps(row)
        ])

    str_query = '\n'.join(bulk_query) + '\n'
    await helpers.async_bulk(es_client, str_query)


def delete_doc(docs: List[dict], index: str) -> Generator:
    for doc in docs:
        yield {
            '_op_type': 'delete',
            '_index': index,
            '_id': doc['id'],
        }


async def delete_es_doc(es_client: AsyncElasticsearch, index: str, doc_id: str):
    try:
        await es_client.delete(index=index, id=doc_id)
        await asyncio.sleep(1)
    except NotFoundError:
        pass


async def delete_all_docs(es_client: AsyncElasticsearch, index: str):
    try:
        await es_client.delete_by_query(index=index, body={"query": {"match_all": {}}})
    except NotFoundError:
        pass


async def get_all_es_docs(es_client: AsyncElasticsearch, index: str):
    query: dict[str, dict] = {
        "query": {
            "match_all": {}
        }
    }

    try:
        doc = await es_client.search(index=index, body=query, size=10000)
    except exceptions.NotFoundError:
        return []

    if not doc:
        return []
    result = doc["hits"]["hits"]

    if not result:
        return []

    return [data["_source"] for data in result]


async def delete_redis_doc(redis_conn, key: str):
    await redis_conn.delete(key)


def generate_doc(docs: List[dict], index: str) -> Generator:
    for doc in docs:
        yield {
            '_index': index,
            '_id': doc['id'],
            '_source': doc
        }


async def upload_film(es_client, film_id: str, title: str):
    index = 'movies'
    data = [{'id': film_id,
             'imdb_rating': 8.5,
             'genre': ['Action', 'Sci-Fi'],
             'title': title,
             'description': 'New World',
             'director': ['Stan'],
             'actors_names': ['Ann', 'Bob'],
             'writers_names': ['Ben', 'Howard'],
             'actors': [
                 {'id': '111', 'name': 'Ann'},
                 {'id': '222', 'name': 'Bob'}
             ],
             'writers': [
                 {'id': '333', 'name': 'Ben'},
                 {'id': '444', 'name': 'Howard'}
             ]}]

    await helpers.async_bulk(es_client, generate_doc(data, index))
    await asyncio.sleep(1)


async def upload_person(es_client, person_id: str, full_name: str):
    index = 'persons'
    data = [{'id': person_id, 'full_name': full_name}]
    await helpers.async_bulk(es_client, generate_doc(data, index))
    await asyncio.sleep(1)


async def upload_genre(es_client, genre_id: str, genre_name: str):
    index = 'genres'
    data = [{'id': genre_id, 'name': genre_name, 'description': "xxx"}]
    await helpers.async_bulk(es_client, generate_doc(data, index))
    await asyncio.sleep(1)


async def get_object(
        session: ClientSession,
        index: str,
        object_id: Union[str, None] = None,
        search_data: Union[dict, None] = None
):
    if index == "movies":
        end_point = "films"
    else:
        end_point = index
    url = f"{cfg.app_host}/api/v1/movies/{end_point}"

    if search_data:
        url += "/search"
    else:
        url += f"/{object_id}"

    async with session.get(url, params=search_data) as response:
        body = await response.json(),
        status = response.status
    print(body[0])
    return status, body[0]
