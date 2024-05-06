from http import HTTPStatus

import pytest
from aiohttp import ClientSession

from utils.services import get_object, upload_genre, delete_redis_doc, delete_es_doc, delete_all_docs


@pytest.mark.asyncio
async def test_genre_by_id_in_es(session: ClientSession, es_client, redis_conn):
    index = "genres"
    genre_id = "472f73f7-4f2c-4129-866a-2ea90bafdc32-genres-id-search"
    genre_name = "genres-id-search"

    redis_key = f"{index}_{genre_id}"

    await delete_all_docs(es_client, index)
    await delete_redis_doc(redis_conn, redis_key)
    status, data = await get_object(session, index, genre_id)

    assert status == HTTPStatus.NOT_FOUND

    await upload_genre(es_client, genre_id, genre_name)
    status, data = await get_object(session, index, genre_id)

    assert status == HTTPStatus.OK
    assert data['id'] == genre_id
    assert data['name'] == genre_name

    await delete_es_doc(es_client, index, genre_id)
    status, data = await get_object(session, index, genre_id)

    assert status == HTTPStatus.OK
    assert data['id'] == genre_id
    assert data['name'] == genre_name

    await delete_redis_doc(redis_conn, redis_key)
    status, data = await get_object(session, index, genre_id)

    assert status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_genre_by_search(session: ClientSession, es_client, redis_conn):
    index = "genres"
    genre_id = "472f73f7-4f2c-4129-866a-2ea90bafdc32-genres-query-search"
    genre_name = "genres-query-search"

    search_data = {"query": genre_name}
    redis_key = f"{index}_25_1_{genre_name}"

    await delete_all_docs(es_client, index)
    await delete_redis_doc(redis_conn, redis_key)
    status, data = await get_object(session, index, search_data=search_data)

    assert status == HTTPStatus.OK
    assert data == []

    await upload_genre(es_client, genre_id, genre_name)
    status, data = await get_object(session, index, search_data=search_data)

    assert status == HTTPStatus.OK
    assert data[0]['id'] == genre_id
    assert data[0]['name'] == genre_name

    await delete_es_doc(es_client, index, genre_id)
    status, data = await get_object(session, index, search_data=search_data)

    assert status == HTTPStatus.OK
    assert data[0]['id'] == genre_id
    assert data[0]['name'] == genre_name

    await delete_redis_doc(redis_conn, redis_key)
    status, data = await get_object(session, index, search_data=search_data)

    assert status == HTTPStatus.OK
    assert data == []
