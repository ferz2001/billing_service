from http import HTTPStatus

REG_NEW_USER_DATA = [(
    {
        "email": "user@example.com",
        "password": "string",
        "login": "string",
        'first_name': 'string',
        'last_name': 'string'
    },
    {
        'status': HTTPStatus.CREATED,
        'response_len': 5
    }
)]
REG_EXIST_USER_DATA = [(
    {
        "email": "test_admin@testadmin.com",
        "password": "string",
        "login": "string",
        'first_name': 'string',
        'last_name': 'string'
    },
    {
        'status': HTTPStatus.CONFLICT,
        'response_len': 1
    }
)]
LOGIN_DATA = [(
    {
        "username": "user@example.com",
        "password": "string",
    },
    {
        'status': HTTPStatus.OK,
        'response_len': 2
    }
)]
FAKE_LOGIN_DATA = [(
    {
        "username": "user@example.com",
        "password": "-------",
    },
    {
        'status': HTTPStatus.UNAUTHORIZED,
        'response_len': 1
    }
)]
TEST_REFRESH_DATA: list = [(
    {},
    {
        'status': HTTPStatus.OK,
        'response_len': 2
    }
)]
