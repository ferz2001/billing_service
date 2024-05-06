import pytest

from tests.functional.settings import settings, pytestmark
from tests.functional.test_data.auth import REG_NEW_USER_DATA, \
    FAKE_LOGIN_DATA, LOGIN_DATA, REG_EXIST_USER_DATA, TEST_REFRESH_DATA


@pytest.mark.parametrize(
    'query_data, expected_answer',
    REG_NEW_USER_DATA
)
@pytestmark
async def test_reg_new_user(
        db_session,
        make_request_with_session,
        query_data,
        expected_answer
):
    # Arrange
    url = f'{settings.app_api_host}auth/signup'

    # Act
    response = await make_request_with_session('post', url, json=query_data)
    data_response = await response.json()

    # Assert
    assert response.status == expected_answer['status']
    assert len(data_response) == expected_answer['response_len']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    REG_EXIST_USER_DATA
)
@pytestmark
async def test_reg_exist_user(
        db_session,
        make_request_with_session,
        query_data,
        expected_answer
):
    # Arrange
    url = f'{settings.app_api_host}auth/signup'

    # Act
    response = await make_request_with_session('post', url, json=query_data)
    data_response = await response.json()

    # Assert
    assert response.status == expected_answer['status']
    assert len(data_response) == expected_answer['response_len']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    LOGIN_DATA
)
@pytestmark
async def test_success_signin(
        make_request_with_session,
        query_data,
        expected_answer
):
    # Arrange
    url = f'{settings.app_api_host}auth/signin'

    # Act
    response = await make_request_with_session('post', url, data=query_data)
    data_response = await response.json()

    # Assert
    assert response.status == expected_answer['status']
    assert len(data_response) == expected_answer['response_len']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    FAKE_LOGIN_DATA
)
@pytestmark
async def test_fake_signin(
        make_request_with_session,
        query_data,
        expected_answer
):
    # Arrange
    url = f'{settings.app_api_host}auth/signin'

    # Act
    response = await make_request_with_session('post', url, data=query_data)
    data_response = await response.json()

    # Assert
    assert response.status == expected_answer['status']
    assert len(data_response) == expected_answer['response_len']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    TEST_REFRESH_DATA
)
@pytestmark
async def test_refresh(
        make_request_with_session,
        query_data,
        expected_answer,
        admin_auth_data
):
    # Arrange
    refresh_token = admin_auth_data['refresh_token']
    url = f'{settings.app_api_host}auth/refresh_tokens'

    # Act
    response = await make_request_with_session(
        'post',
        url,
        json={'refresh_token': refresh_token}
    )
    data_response = await response.json()

    # Assert
    assert response.status == expected_answer['status']
    assert len(data_response) == expected_answer['response_len']
