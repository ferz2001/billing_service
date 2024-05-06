from typing import Dict, Union

import pytest

from tests.functional.settings import settings, pytestmark
from tests.functional.test_data.roles import (
    GET_ROLES_POSITIVE_DATA,
    GET_ROLES_NEGATIVE_DATA,
    CREATE_ROLE_POSITIVE_DATA,
    CREATE_ROLE_NEGATIVE_DATA,
    CHANGE_ROLE_POSITIVE_DATA,
    CHANGE_ROLE_NEGATIVE_DATA,
    DELETE_ROLE_POSITIVE_DATA,
    DELETE_ROLE_NEGATIVE_DATA,
    SET_USER_ROLE_POSITIVE_DATA,
    SET_USER_ROLE_NEGATIVE_DATA,
    DELETE_USER_ROLE_POSITIVE_DATA,
    GET_MY_ROLES_POSITIVE_DATA
)


@pytest.mark.parametrize(
    'query_data, expected_answer',
    GET_ROLES_POSITIVE_DATA
)
@pytestmark
async def test_positive_get_roles(
        admin_auth_header,
        make_request_with_session,
        query_data,
        expected_answer
):
    # Arrange
    url = f'{settings.app_api_host}roles'

    # Act
    response = await make_request_with_session(
        'get',
        url,
        headers=admin_auth_header
    )
    data_response = await response.json()

    # Assert
    assert response.status == expected_answer.get('status')
    assert data_response[1].get('name') == expected_answer.get(
        'full_return').get('admin')
    assert data_response[0].get('name') == expected_answer.get(
        'full_return').get('user')


@pytest.mark.parametrize(
    'query_data, expected_answer',
    GET_ROLES_NEGATIVE_DATA
)
@pytestmark
async def test_negative_get_roles(
        make_request_with_session,
        query_data,
        expected_answer,
):
    # Arrange
    url = f'{settings.app_api_host}roles'

    # Act
    response = await make_request_with_session(
        'get',
        url,
        headers={}
    )

    # Assert
    assert response.status == expected_answer.get('status')


@pytest.mark.parametrize(
    'query_data, expected_answer',
    CREATE_ROLE_POSITIVE_DATA
)
@pytestmark
async def test_positive_create_role(
        admin_auth_header,
        make_request_with_session,
        query_data,
        expected_answer,
):
    # Arrange
    url = f'{settings.app_api_host}roles'

    # Act
    response = await make_request_with_session(
        'post',
        url,
        json=query_data,
        headers=admin_auth_header
    )
    data_response = await response.json()

    # Assert
    assert response.status == expected_answer.get('status')
    assert len(data_response) == expected_answer.get('length')
    assert data_response.get('name') == expected_answer.get('full_return').get(
        'name')


@pytest.mark.parametrize(
    'query_data, expected_answer',
    CREATE_ROLE_NEGATIVE_DATA
)
@pytestmark
async def test_negative_create_role(
        admin_auth_header,
        make_request_with_session,
        query_data,
        expected_answer,
):
    # Arrange
    url = f'{settings.app_api_host}roles'

    # Act
    response = await make_request_with_session(
        'post',
        url,
        json=query_data,
        headers={}
    )

    # Assert
    assert response.status == expected_answer.get('status')


@pytest.mark.parametrize(
    'query_data, expected_answer',
    CHANGE_ROLE_POSITIVE_DATA
)
@pytestmark
async def test_positive_change_role(
        admin_auth_header,
        make_request_with_session,
        query_data,
        expected_answer,
):
    # Arrange
    put_query_data = {
        'name': query_data.get('json').get('name'),
        'new_name': query_data.get('json').get('new_name'),
        'new_description': query_data.get('json').get('new_description'),
    }
    url = f'{settings.app_api_host}roles'

    # Act
    response = await make_request_with_session(
        'put',
        url,
        params=put_query_data,
        headers=admin_auth_header
    )

    # Assert
    assert response.status == expected_answer.get('status')


@pytest.mark.parametrize(
    'query_data, expected_answer',
    CHANGE_ROLE_NEGATIVE_DATA
)
@pytestmark
async def test_negative_change_role(
        make_request_with_session,
        query_data,
        expected_answer,
):
    # Arrange
    url = f'{settings.app_api_host}roles'
    put_query_data = {
        'name': query_data.get('json').get('name'),
        'new_name': query_data.get('json').get('new_name'),
        'new_description': query_data.get('json').get('new_description'),
    }

    # Act
    response = await make_request_with_session(
        'put',
        url,
        params=put_query_data,
    )

    # Assert
    assert response.status == expected_answer.get('status')


@pytest.mark.parametrize(
    'query_data, expected_answer',
    DELETE_ROLE_POSITIVE_DATA
)
@pytestmark
async def test_positive_delete_role(
        admin_auth_header,
        make_request_with_session,
        query_data,
        expected_answer,
):
    delete_query_data = {
        'name': query_data.get('json').get('name'),
    }
    url = f'{settings.app_api_host}roles'
    response = await make_request_with_session(
        'delete',
        url,
        params=delete_query_data,
        headers=admin_auth_header
    )

    assert response.status == expected_answer.get('status')


@pytest.mark.parametrize(
    'query_data, expected_answer',
    DELETE_ROLE_NEGATIVE_DATA
)
@pytestmark
async def test_negative_delete_role(
        make_request_with_session,
        query_data,
        expected_answer,
):
    url = f'{settings.app_api_host}roles'
    delete_query_data = {
        'name': query_data.get('name'),
    }
    response = await make_request_with_session(
        'delete',
        url,
        params=delete_query_data
    )

    assert response.status == expected_answer.get('status')


@pytest.mark.parametrize(
    'query_data, expected_answer',
    SET_USER_ROLE_POSITIVE_DATA
)
@pytestmark
async def test_positive_set_user_role(
        admin_auth_header,
        make_request_with_session,
        query_data,
        expected_answer,
):
    set_query_data = {
        'email': query_data.get('auth').get('email'),
        'role_name': query_data.get('json').get('role_name'),
    }
    url = f'{settings.app_api_host}roles/user'
    response = await make_request_with_session(
        'post',
        url,
        params=set_query_data,
        headers=admin_auth_header
    )
    data_response = await response.json()

    assert response.status == expected_answer.get('status')
    assert len(data_response) == expected_answer.get('length')


@pytest.mark.parametrize(
    'query_data, expected_answer',
    SET_USER_ROLE_NEGATIVE_DATA
)
@pytestmark
async def test_negative_set_user_role(
        make_request_with_session,
        query_data: Dict[str, Union[str, int, float, None]],
        expected_answer: Dict[str, Union[str, int, float, None]],
):
    url = f'{settings.app_api_host}roles'
    delete_query_data = {
        'role_name': query_data.get('role_name'),
        'email': query_data.get('email'),
    }
    response = await make_request_with_session(
        'post',
        url,
        params=delete_query_data
    )

    assert response.status == expected_answer.get('status')


@pytest.mark.parametrize(
    'query_data, expected_answer',
    DELETE_USER_ROLE_POSITIVE_DATA
)
@pytestmark
async def test_positive_delete_user_role(
        make_request_with_session,
        admin_auth_header,
        query_data,
        expected_answer,
):
    set_query_data = {
        'email': query_data.get('auth').get('email'),
        'role_name': query_data.get('json').get('role_name'),
    }

    url = f'{settings.app_api_host}roles/user'
    response = await make_request_with_session(
        'delete',
        url,
        params=set_query_data,
        headers=admin_auth_header
    )

    assert response.status == expected_answer.get('status')


@pytest.mark.parametrize(
    'query_data, expected_answer',
    GET_MY_ROLES_POSITIVE_DATA
)
@pytestmark
async def test_positive_get_my_roles(
        admin_auth_header,
        make_request_with_session,
        query_data,
        expected_answer,
):
    url = f'{settings.app_api_host}roles/me'
    response = await make_request_with_session(
        'get',
        url,
        headers=admin_auth_header
    )
    data_response = await response.json()

    assert response.status == expected_answer.get('status')
    assert data_response == expected_answer.get('full_return')
