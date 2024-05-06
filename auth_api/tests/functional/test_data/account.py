from http import HTTPStatus

CHANGE_LOGIN_DATA = {
    'new_login': 'NewLogin'
}

LOGIN_DATA_BEFORE_CHANGE_PASS = [(
    {
        "username": "test_chenge_pass@mail.com",
        "password": "string",
    },
    {
        'status': HTTPStatus.OK,
    }
)]
