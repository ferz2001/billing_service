from http import HTTPStatus

GET_ROLES_POSITIVE_DATA = [
    (
        {
            'email': 'test_admin@testadmin.com', 'password': 'test_admin'
        },
        {
            'status': HTTPStatus.ACCEPTED, 'length': 2,
            'full_return': {
                'admin': 'admin',
                'user': 'user'
            }
        }
    )
]

GET_ROLES_NEGATIVE_DATA: list = [
    (
        {},
        {
            'status': HTTPStatus.UNAUTHORIZED
        }
    )
]

CREATE_ROLE_POSITIVE_DATA = [
    (
        {
            "name": "test",
            "description": "test"
        },
        {
            'status': HTTPStatus.ACCEPTED, 'length': 2,
            'full_return': {
                'name': 'test',
                'description': 'test'
            }
        }
    )
]

CREATE_ROLE_NEGATIVE_DATA = [
    (
        {
            'name': 'test', 'description': 'test'
        },
        {
            'status': HTTPStatus.UNAUTHORIZED
        }
    )
]

CHANGE_ROLE_POSITIVE_DATA = [
    (
        {
            "auth": {'email': 'test_admin@testadmin.com',
                     'password': 'test_admin'},
            "json": {'name': 'test', 'new_name': 'test1',
                     'new_description': 'test1'}
        },
        {
            'status': HTTPStatus.ACCEPTED
        }
    )
]

CHANGE_ROLE_NEGATIVE_DATA = [
    (
        {
            "json": {'name': 'test', 'new_name': 'test1',
                     'new_description': 'test1'}
        },
        {
            'status': HTTPStatus.UNAUTHORIZED
        }
    )
]

DELETE_ROLE_POSITIVE_DATA = [
    (
        {
            'auth': {'email': 'test_admin@testadmin.com',
                     'password': 'test_admin'},
            'json': {'name': 'test1'}
        },
        {
            'status': HTTPStatus.ACCEPTED
        }
    )
]

DELETE_ROLE_NEGATIVE_DATA = [
    (
        {
            'name': 'test1'
        },
        {
            'status': HTTPStatus.UNAUTHORIZED
        }
    )
]

SET_USER_ROLE_POSITIVE_DATA = [
    (
        {
            'auth': {'email': 'test_admin@testadmin.com',
                     'password': 'test_admin'},
            'json': {'role_name': 'user'}
        },
        {
            'status': HTTPStatus.ACCEPTED, 'length': 2,
            'full_return': [
                {'name': 'user', 'description': 'user'},
                {'name': 'admin', 'description': 'admin'},
            ]
        }
    )
]

SET_USER_ROLE_NEGATIVE_DATA = [
    (
        {
            'role_name': 'user', 'email': 'test_admin@testadmin.com'
        },
        {
            'status': HTTPStatus.UNAUTHORIZED
        }
    )
]

DELETE_USER_ROLE_POSITIVE_DATA = [
    (
        {
            'auth': {'email': 'test_admin@testadmin.com',
                     'password': 'test_admin'},
            'json': {'role_name': 'user'}
        },
        {
            'status': HTTPStatus.ACCEPTED
        }
    )
]

GET_MY_ROLES_POSITIVE_DATA = [
    (
        {
            'auth': {'email': 'test_admin@testadmin.com',
                     'password': 'test_admin'}
        },
        {
            'status': HTTPStatus.ACCEPTED, 'full_return': ["admin"]
        }
    )
]
