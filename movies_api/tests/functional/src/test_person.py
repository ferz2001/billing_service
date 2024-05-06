from http import HTTPStatus

import pytest
from aiohttp import ClientSession

from utils.services import get_object, upload_person, delete_redis_doc, delete_es_doc, delete_all_docs


@pytest.mark.asyncio
async def test_person_by_id_in_es(session: ClientSession, es_client, redis_conn):
    index = "persons"
    person_id = "472f73f7-4f2c-4129-866a-2ea90bafdc32-persons-id-search"
    full_name = "persons-id-search"

    redis_key = f"{index}_{person_id}"

    await delete_all_docs(es_client, index)
    await delete_redis_doc(redis_conn, redis_key)
    status, data = await get_object(session, index, person_id)

    assert status == HTTPStatus.NOT_FOUND

    await upload_person(es_client, person_id, full_name)
    status, data = await get_object(session, index, person_id)

    assert status == HTTPStatus.OK
    assert data['id'] == person_id
    assert data['full_name'] == full_name

    await delete_es_doc(es_client, index, person_id)
    status, data = await get_object(session, index, person_id)

    assert status == HTTPStatus.OK
    assert data['id'] == person_id
    assert data['full_name'] == full_name

    await delete_redis_doc(redis_conn, redis_key)
    status, data = await get_object(session, index, person_id)

    assert status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_person_by_search(session: ClientSession, es_client, redis_conn):
    index = "persons"
    person_id = "472f73f7-4f2c-4129-866a-2ea90bafdc32-persons-query-search"
    full_name = "persons-query-search"

    search_data = {"query": full_name}
    redis_key = f"{index}_25_1_{full_name}"

    await delete_all_docs(es_client, index)
    await delete_redis_doc(redis_conn, redis_key)
    status, data = await get_object(session, index, search_data=search_data)

    assert status == HTTPStatus.OK
    assert data == []

    await upload_person(es_client, person_id, full_name)
    status, data = await get_object(session, index, search_data=search_data)

    assert status == HTTPStatus.OK
    assert data[0]['id'] == person_id
    assert data[0]['full_name'] == full_name

    await delete_es_doc(es_client, index, person_id)
    status, data = await get_object(session, index, search_data=search_data)

    assert status == HTTPStatus.OK
    assert data[0]['id'] == person_id
    assert data[0]['full_name'] == full_name

    await delete_redis_doc(redis_conn, redis_key)
    status, data = await get_object(session, index, search_data=search_data)

    assert status == HTTPStatus.OK
    assert data == []
