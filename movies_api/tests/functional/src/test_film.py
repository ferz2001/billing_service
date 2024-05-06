import uuid
from http import HTTPStatus

import pytest
from aiohttp import ClientSession

from utils.services import get_object, upload_film, delete_redis_doc, delete_es_doc, delete_all_docs


@pytest.mark.asyncio
async def test_films_by_id_in_es(session: ClientSession, es_client, redis_conn):
    # Arrange
    index = "movies"
    film_id = str(uuid.uuid4())
    film_title = "movies-id-search"
    redis_key = f"{index}_{film_id}"

    # Act
    await delete_all_docs(es_client, index)
    await delete_redis_doc(redis_conn, redis_key)
    status, data = await get_object(session, index, film_id)

    assert status == HTTPStatus.UNAUTHORIZED

    # Act
    await upload_film(es_client, film_id, film_title)
    status, data = await get_object(session, index, film_id)

    assert status == HTTPStatus.UNAUTHORIZED

    # Act
    await delete_es_doc(es_client, index, film_id)
    status, data = await get_object(session, index, film_id)

    assert status == HTTPStatus.UNAUTHORIZED

    # Act
    await delete_redis_doc(redis_conn, redis_key)
    status, data = await get_object(session, index, film_id)

    assert status == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_films_by_search(session: ClientSession, es_client, redis_conn):
    index = "movies"
    film_id = str(uuid.uuid4())
    film_title = "movies-query-search"
    search_data = {"query": film_title}
    redis_key = f"{index}_25_1_{film_title}"

    await delete_all_docs(es_client, index)
    await delete_redis_doc(redis_conn, redis_key)
    status, data = await get_object(session, index, search_data=search_data)

    assert status == HTTPStatus.OK

    await upload_film(es_client, film_id, film_title)
    status, data = await get_object(session, index, search_data=search_data)

    assert status == HTTPStatus.OK
    assert data[0]['id'] == film_id
    assert data[0]['title'] == film_title

    await delete_es_doc(es_client, index, film_id)
    status, data = await get_object(session, index, search_data=search_data)

    assert status == HTTPStatus.OK
    assert data[0]['id'] == film_id
    assert data[0]['title'] == film_title

    await delete_redis_doc(redis_conn, redis_key)
    status, data = await get_object(session, index, search_data=search_data)

    assert status == HTTPStatus.OK
    assert data == []
