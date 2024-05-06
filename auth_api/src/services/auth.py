import abc
import logging
import uuid
from datetime import timedelta, datetime, timezone
from functools import lru_cache
from typing import Union

from fastapi import Depends, status, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from redis.asyncio import Redis
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from db.postgres import get_session, DbService
from db.redis import get_redis
from models.base import TokenPair, User
from schemas.base import SignUpUser, Tokens, RefreshToken, SignInUser, SignInUserResponse



logger = logging.getLogger('auth_api.services.auth')


class AbstractAsyncAuthService(abc.ABC):
    @abc.abstractmethod
    async def create_user(self, signup_user: SignUpUser) -> User:
        pass
    
    @abc.abstractmethod
    async def signin(self, form_data: SignInUser,
                     request: Request) -> Tokens:
        pass
    
    @abc.abstractmethod
    async def update_token_pair(self, token: RefreshToken) -> Tokens:
        pass
    
    @abc.abstractmethod
    async def check_token(self, token: str, token_type: str) -> dict:
        pass


class AuthService(AbstractAsyncAuthService):
    def __init__(self, db_service: DbService, redis: Redis) -> None:
        self.db_service = db_service
        self.redis = redis
    
    async def create_user(self, signup_user: SignUpUser) -> User:
        try:
            return await self.db_service.insert(User,
                                                signup_user.dict())
        except IntegrityError:
            logger.error('User already exists with data %s', signup_user.dict())
            raise HTTPException(status.HTTP_409_CONFLICT,
                                'User with login or email already exists.')
    
    async def get_db_user_by_email(self, email: str) -> User:
        result = await self.db_service.select(User,
                                              [(User.email, email)])
        if not result:
            logger.error('User does not exist with email %s', email)
            raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                                'User with email not found.')
        return result[0]
    
    async def create_db_token_pair(self, user_id: str, jti: uuid.UUID,
                                   user_agent: Union[str, None]) -> TokenPair:
        data: dict[str, Union[Union[str, uuid.UUID], None]] = {}
        data.update(user_id=user_id)
        data.update(user_agent=user_agent)
        data.update(jti=jti)
        logger.info('Creating db token with data %s', data)
        return await self.db_service.insert(TokenPair, data)
    
    async def signin(self, form_data: SignInUser,
                     request: Request) -> SignInUserResponse:

        from services.roles import RolesService

        user: User = await self.get_db_user_by_email(form_data.username)
        if not user.check_password(form_data.password):
            logger.error('Invalid user password %s', form_data.password)
            raise HTTPException(status.HTTP_401_UNAUTHORIZED,
                                "Login or Password not valid.")
        
        user_agent = request.headers.get('User-Agent')
        if user_agent is None:
            logging.error('User agent is undefined [%s]', request)
            raise HTTPException(status.HTTP_400_BAD_REQUEST, 'User agent is undefined.')

        tokens = await self.create_new_tokens(user, user_agent)
        roles = await RolesService(db_service=self.db_service).get_user_roles(user)

        return SignInUserResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            id=user.id,
            email=user.email,
            roles=roles,
            first_name=user.first_name,
            last_name=user.last_name
        )
    
    @staticmethod
    def create_token(token_type: str, data: dict, expires_min: int, jti: uuid.UUID):
        to_encode = data.copy()
        expires_delta = timedelta(minutes=expires_min)
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update(
            {'jti': str(jti), 'exp': expire, 'token_type': token_type})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY,
                                 algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
    
    async def create_access_token(self, user: User, jti: uuid.UUID) -> str:
        user_id = str(user.id)
        token_data = {'user_id': user_id, 'email': user.email}
        return self.create_token('access', token_data,
                                 settings.ACCESS_TOKEN_EXPIRES_IN, jti)
    
    async def create_refresh_token(self, user: User, jti: uuid.UUID) -> str:
        user_id = str(user.id)
        token_data = {'user_id': user_id}
        return self.create_token('refresh', token_data,
                                 settings.REFRESH_TOKEN_EXPIRES_IN, jti)
    
    async def create_tokens(self, user: User) -> tuple[Tokens, uuid.UUID]:
        jti = uuid.uuid4()
        tokens = Tokens(
            refresh_token=await self.create_refresh_token(user, jti),
            access_token=await self.create_access_token(user, jti),
        )
        return tokens, jti
    
    async def create_new_tokens(self, user: User, user_agent: Union[str, None]) -> Tokens:
        tokens_data = await self.create_tokens(user)
        tokens = tokens_data[0]
        await self.create_db_token_pair(user.id, tokens_data[1], user_agent)
        return tokens
    
    async def update_token_pair(self, token: RefreshToken) -> Tokens:
        payload = await self.check_token(token.refresh_token, 'refresh')
        data_user = await self.db_service.select(
            what_select=User,
            where_select=[(User.id, payload['user_id'])],
        )
        user = data_user[0]
        tokens_data = await self.create_tokens(user)
        tokens = tokens_data[0]
        new_jti = tokens_data[1]
        await self.set_jti_in_deny_list(payload['jti'])
        await self.db_service.update(TokenPair, {'jti': new_jti},
                                     [TokenPair.jti, payload['jti']])
        return tokens
    
    async def set_jti_in_deny_list(self, jti: uuid.UUID):
        """
        Установка токена доступа как разлогиненного.

        :param jti: id токенов.
        """
        logger.debug('Setting jti [%s] in deny list', str(jti))
        await self.redis.set(str(jti), 'logout')
        expire_in = settings.REFRESH_TOKEN_EXPIRES_IN * 60
        logger.debug('Setting jti [%s] expire in [%s]', str(jti), expire_in)
        await self.redis.expire(str(jti), expire_in)
    
    async def is_token_in_deny_list(self, jti: uuid.UUID) -> bool:
        return bool(
            await self.redis.exists(str(jti))
        )
    
    async def check_token(self, token: str, token_type: str) -> dict:
        """
        Function that does something interesting.

        Args:
            - token_type - 'access' or 'refresh'
        Returns:
            - payload - dict
        """
        error = HTTPException(status.HTTP_401_UNAUTHORIZED,
                              f'{token_type} not valid')
        
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY,
                                 algorithms=[settings.JWT_ALGORITHM])
            logger.debug('JWT decoded - %s', payload)
        except JWTError:
            logger.error('JWT error - %s [%s]', token, token_type)
            raise error
        
        if payload['token_type'] != token_type:
            logger.error('JWT error - token_type [%s] != [%s]', payload['token_type'], token_type)
            raise error
        
        jti = payload['jti']
        if await self.is_token_in_deny_list(jti):
            logger.info('JWT token with %s exists in deny list', jti)
            raise error
        
        return payload


@lru_cache()
def get_auth_service(
        db: AsyncSession = Depends(get_session),
        redis: Redis = Depends(get_redis),
) -> AuthService:
    return AuthService(
        db_service=DbService(db=db),
        redis=redis,
    )


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/signin")


async def get_current_user(
        auth_service: AuthService = Depends(get_auth_service),
        token=Depends(oauth2_scheme),
) -> User:
    payload = await auth_service.check_token(token, 'access')
    return await auth_service.get_db_user_by_email(payload['email'])
