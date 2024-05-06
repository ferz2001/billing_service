import uuid
from functools import lru_cache
from http import HTTPStatus
from typing import Union

from aioauth_client import YandexClient, GoogleClient, VKClient, OAuth2Client
from fastapi import Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import oauth_settings
from db.postgres import get_session, DbService
from db.redis import get_redis
from models.base import SocialAccount, User
from schemas.base import Tokens, SignUpUser
from services.auth import AuthService

providers = {
    'yandex': YandexClient(
        client_id=oauth_settings.yandex_client_id,
        client_secret=oauth_settings.yandex_client_secret,
    ),
    'vk': VKClient(
        client_id=oauth_settings.vk_client_id,
        client_secret=oauth_settings.vk_client_secret,
        redirect_uri=oauth_settings.vk_redirect_uri,
    ),
    'google': GoogleClient(
        client_id=oauth_settings.google_client_id,
        client_secret=oauth_settings.google_client_secret,
        redirect_uri=oauth_settings.google_redirect_uri,
        scope=oauth_settings.google_scope,
    ),
}


class SocialAuthService(AuthService):
    @staticmethod
    def get_provider_by_name(provider_name: str) -> OAuth2Client:
        if provider_name in providers:
            return providers[provider_name]
        else:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND,
                detail="Provider doesn't exist",
            )

    def get_login_url(self, provider_name: str) -> str:
        provider = self.get_provider_by_name(provider_name)
        return provider.get_authorize_url()

    async def delete_social_account(self, user: User, id_in_db: uuid.UUID):
        account_data = await self.db_service.simple_select(
            SocialAccount,
            [
                (SocialAccount.user_id, user.id),
                (SocialAccount.id, id_in_db),
            ],
        )
        if account_data:
            await self.db_service.delete(
                what_delete=SocialAccount,
                where_delete=[(SocialAccount.id, id_in_db)],
            )
        else:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Social Account with id doesn't exist",
            )

    async def social_accounts(self, user: User) -> list[SocialAccount]:
        return await self.db_service.select(
            SocialAccount,
            [(SocialAccount.user_id, user.id)],
        )

    async def create_empty_user(self, email: Union[str, None] = None) -> User:
        signup_user = SignUpUser(
            login=str(uuid.uuid4()),
            email=email if email else str(uuid.uuid4()) + '@example.com',
            password=str(uuid.uuid4()),
            first_name=None,
            last_name=None,
        )

        return await self.db_service.insert(User, signup_user.dict())

    async def create_social_user(
            self,
            social_name,
            social_id,
            email=None,
    ) -> User:
        if email:
            user_data = await self.db_service.select(
                User, [(User.email, email)],
            )
            if not user_data:
                user = await self.create_empty_user(email)
            else:
                user = user_data[0]
        else:
            user = await self.create_empty_user()

        await self.db_service.insert(SocialAccount, {
            'user_id': user.id,
            'social_id': social_id,
            'social_name': social_name,
        })
        return user

    @staticmethod
    def get_email_from_data(data: dict) -> Union[str, None]:
        if 'email' in data:
            return data['email']
        elif 'default_email' in data:
            return data['default_email']
        else:
            return None

    async def auth(
            self,
            provider_name: str,
            code: str,
    ) -> Tokens:
        provider = self.get_provider_by_name(provider_name)
        token, _ = await provider.get_access_token(code)
        user, data = await provider.user_info()
        social_name = provider.name
        social_id = data['id']
        email = self.get_email_from_data(data)

        social_user_data = await self.db_service.select(
            SocialAccount,
            [(SocialAccount.social_id, social_id),
             (SocialAccount.social_name, social_name)],
        )
        if not social_user_data:
            user = await self.create_social_user(
                social_name, social_id, email)
        else:
            social_user: SocialAccount = social_user_data[0]
            user_data = await self.db_service.select(
                User, [(User.id, social_user.user_id)],
            )
            user = user_data[0]

        return await self.create_new_tokens(user, social_name)


@lru_cache()
def get_social_auth_service(
        db: AsyncSession = Depends(get_session),
        redis: Redis = Depends(get_redis),
) -> SocialAuthService:
    return SocialAuthService(
        db_service=DbService(db=db),
        redis=redis,
    )
