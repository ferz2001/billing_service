import abc
import uuid
from functools import lru_cache

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from redis.asyncio import Redis

from core.config import settings
from db.redis import get_redis


class UnAuthException(BaseException):
    pass


class AbstractAsyncAuthService(abc.ABC):
    @abc.abstractmethod
    async def check_token(self, token: str, token_type: str) -> dict:
        pass


class AuthService(AbstractAsyncAuthService):
    def __init__(self, redis: Redis):
        self.redis = redis

    async def check_check_token_in_deny_list(self, jti: uuid.UUID) -> bool:
        value = await self.redis.get(str(jti))
        if value:
            return True
        else:
            return False

    async def check_token(self, token: str, token_type: str) -> dict:
        try:
            payload = jwt.decode(token, settings.jwt_secret_key,
                                 algorithms=[settings.jwt_algorithm])
        except JWTError:
            raise UnAuthException

        if payload['token_type'] != token_type:
            raise UnAuthException

        jti = payload['jti']
        if await self.check_check_token_in_deny_list(jti):
            raise UnAuthException

        return payload


@lru_cache()
def get_auth_service(
        redis: Redis = Depends(get_redis),
) -> AuthService:
    return AuthService(
        redis=redis,
    )


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/signin")


async def get_current_user_data(
        auth_service: AuthService = Depends(get_auth_service),
        token=Depends(oauth2_scheme),
) -> dict:
    try:
        payload = await auth_service.check_token(token, 'access')
    except UnAuthException:
        raise HTTPException(status_code=403, detail='Token not valid')
    return payload
