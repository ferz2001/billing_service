import asyncio
from typing import AsyncGenerator, Union

import aiohttp
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, \
    AsyncSession

from tests.functional.settings import settings


@pytest_asyncio.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


async def db_prepare(async_session: async_sessionmaker):
    async with async_session.begin() as session:
        await session.execute(text("""DELETE FROM public.userrole;"""))
        await session.execute(text("""DELETE FROM public.token_pair;"""))
        await session.execute(text("""DELETE FROM public.user;"""))
        await session.execute(text("""DELETE FROM public.role;"""))
        await session.execute(text("""
                        INSERT INTO "user" (id, login, password, email)
                        VALUES (:user_id, 'change_pass', 'pbkdf2:sha256:260000$cMXDbLOueC2t9PYg$fdb8acc35241d65abf17c2926bd223a62b48c95412765905c1ce880fd5d6e66d', 'test_chenge_pass@mail.com')
                    """), {'user_id': 'fd950918-9191-4101-96e7-621c85ad17f0'})
        await session.execute(text("""
                INSERT INTO role (id, name, description)
                VALUES (:role_id_user, 'user', 'user')
            """), {
            'role_id_user': '5e38cf80-537f-4a6a-a2e1-b68616b88a8f'})
        await session.execute(text("""
                INSERT INTO role (id, name, description)
                VALUES (:role_id_admin, 'admin', 'admin')
            """), {
            'role_id_admin': '28c3eb89-7c87-4382-8555-330a808f9a8d'})
        await session.execute(text("""
                INSERT INTO "user" (id, login, password, email)
                VALUES (:user_id, 'test_admin', 'pbkdf2:sha256:260000$diVv1dHphxjty55A$30d64abb18c307ca9447db11ead8353ff10662987fea522fe8d18019c22ff3a3', 'test_admin@testadmin.com')
            """), {'user_id': 'c058891a-34ce-4985-b252-5ed1cd4497b4'})
        await session.execute(text("""
                INSERT INTO userrole (id, user_id, role_id)
                VALUES (:user_role_id, :user_id, :role_id_admin)
            """), {
            'user_role_id': 'e0b42c00-4e0b-46ad-8f59-d7d3c9b9e777',
            'role_id_admin': '28c3eb89-7c87-4382-8555-330a808f9a8d',
            'user_id': 'c058891a-34ce-4985-b252-5ed1cd4497b4'})
        await session.commit()


@pytest_asyncio.fixture(name='db_session', scope='session')
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(settings.dsl_database, echo=False,
                                 future=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    await db_prepare(async_session)

    async with async_session() as session:
        yield session


# # @pytest.fixture(scope='session', autouse=True)
# # def setup_db_session():
# #     db_prepare_test_data()
# #
#
# # @pytest.fixture(scope='session')
# # def anyio_backend():
# #     return "asyncio"
# #
#
# @pytest.fixture(scope='session')
# async def http_client():
#     async with aiohttp.ClientSession() as client:
#         yield client
#
#

#
#
@pytest_asyncio.fixture(name='make_request_with_session',
                        scope='function')
def make_request_with_session():
    async def inner(method: str, query: str, params: Union[dict, None] = None,
                    headers: Union[dict, None] = None, data: Union[dict, None] = None,
                    json: Union[dict, None] = None):
        async with aiohttp.ClientSession() as session:
            resp = await session.__getattribute__(method)(query, data=data,
                                                          json=json,
                                                          headers=headers,
                                                          params=params)
            return resp

    return inner


@pytest_asyncio.fixture(name='admin_auth_data')
async def admin_auth_data(db_session, make_request_with_session) -> dict:
    url = f'{settings.app_api_host}auth/signin'
    response = await make_request_with_session('post', url, data={
        'username': 'test_admin@testadmin.com', 'password': 'test_admin'
    })
    return await response.json()


@pytest_asyncio.fixture(name='admin_auth_header')
async def admin_auth_header(admin_auth_data) -> dict:
    return {'Authorization': 'Bearer ' + admin_auth_data.get('access_token')}
