from functools import wraps
from http import HTTPStatus

import aiohttp
from fastapi import HTTPException, Request
from core.config import cfg


async def request_post(url, headers=None, query_params=None):
    async with aiohttp.ClientSession(headers=headers) as session:
        try:
            async with session.post(url, params=query_params) as response:
                if response.status != HTTPStatus.OK:
                    message = await response.json()
                    raise HTTPException(
                        status_code=HTTPStatus.UNAUTHORIZED,
                        detail=message,
                    )
                return await response.json()
        except aiohttp.ServerConnectionError:
            return HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)


def auth_required(func):
    @wraps(func)
    async def wrapper(*args, request: Request, **kwargs):
        auth_header = request.headers.get('authorization', None)
        if not auth_header:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="Authorization token is not provide",
            )
        query_params = {'access_token': auth_header.split()[1]}
        await request_post(f'{cfg.auth_url}/api/v1/auth/validate_token', query_params=query_params)

        result = await func(*args, request=request, **kwargs)
        return result
    return wrapper
