from http import HTTPStatus

import pytest

from tests.functional.settings import settings, pytestmark
from tests.functional.test_data.account import CHANGE_LOGIN_DATA, \
    LOGIN_DATA_BEFORE_CHANGE_PASS


@pytestmark
async def test_logout_me(
        admin_auth_header,
        make_request_with_session,
):
    # Arrange
    url = f'{settings.app_api_host}account/logout_me'

    # Act
    await make_request_with_session(
        'post', url, headers=admin_auth_header
    )
    response = await make_request_with_session(
        'post', url, headers=admin_auth_header
    )

    # Assert
    assert response.status == HTTPStatus.UNAUTHORIZED


@pytestmark
async def test_logout_all_devices(
        admin_auth_header,
        make_request_with_session,
):
    # Arrange
    url = f'{settings.app_api_host}account/logout_all_devices'

    # Act
    await make_request_with_session(
        'post', url, headers=admin_auth_header
    )
    response = await make_request_with_session(
        'post', url, headers=admin_auth_header
    )

    # Assert
    assert response.status == HTTPStatus.UNAUTHORIZED


@pytestmark
async def test_change_login_fake_user(
        admin_auth_header,
        make_request_with_session,
):
    # Arrange
    url = f'{settings.app_api_host}account/change_login'

    # Act
    response = await make_request_with_session(
        'put', url, json=CHANGE_LOGIN_DATA
    )

    # Assert
    assert response.status == HTTPStatus.UNAUTHORIZED


@pytestmark
async def test_change_login_user(
        admin_auth_header,
        make_request_with_session,
):
    url = f'{settings.app_api_host}account/change_login'

    response = await make_request_with_session(
        'put', url, json=CHANGE_LOGIN_DATA, headers=admin_auth_header
    )
    data_response = await response.json()

    assert response.status == HTTPStatus.OK
    assert data_response['login'] == CHANGE_LOGIN_DATA['new_login']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    LOGIN_DATA_BEFORE_CHANGE_PASS
)
@pytestmark
async def test_change_password_fake_user(
        make_request_with_session,
        query_data,
        expected_answer,

):
    # Arrange
    sign_in_url = f'{settings.app_api_host}auth/signin'
    change_password_url = f'{settings.app_api_host}account/change_password'

    # Act
    response = await make_request_with_session(
        'post', sign_in_url, data=query_data)
    data_response = await response.json()
    new_pass = 'qwe123qwe123'
    await make_request_with_session(
        'put', change_password_url, json={'new_password': new_pass},
        headers={
            'Authorization': 'Bearer ' + data_response.get('access_token')
        }
    )
    response = await make_request_with_session(
        'post', sign_in_url, data={
            'username': query_data['username'],
            'password': new_pass
        })

    # Assert
    assert response.status == expected_answer['status']


@pytestmark
async def test_history_fake_user(
        make_request_with_session,
):
    # Arrange
    url = f'{settings.app_api_host}account/login_history'

    # Act
    response = await make_request_with_session('post', url, params={'page': 1})
    data_response = await response.json()
    assert response.status == HTTPStatus.UNAUTHORIZED
    assert len(data_response) == 1


@pytestmark
async def test_history_user(
        admin_auth_header,
        make_request_with_session,
):
    url = f'{settings.app_api_host}account/login_history'

    response = await make_request_with_session('post', url, params={'page': 1},
                                               headers=admin_auth_header)
    data_response = await response.json()

    assert response.status == HTTPStatus.OK
    assert len(data_response) >= 1
