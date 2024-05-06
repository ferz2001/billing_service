from http import HTTPStatus

from fastapi import HTTPException


async def object_details(obj):
    if not obj:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Object not found')
    else:
        return obj
