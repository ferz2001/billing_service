from fastapi import APIRouter, Depends, status
from fastapi.responses import RedirectResponse
from schemas.base import Tokens
from services.oauth import get_social_auth_service, \
    SocialAuthService

router = APIRouter()


@router.get(
    '/login/{provider_name}',
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    description='Ссылка на авторизацию через провайдера (vk, yandex, google)',
    tags=["Social Auth"],
)
async def oauth_login(provider_name: str,
                      social_auth_service: SocialAuthService = Depends(
                          get_social_auth_service)):
    return RedirectResponse(social_auth_service.get_login_url(provider_name))


@router.get(
    '/auth/{provider_name}',
    response_model=Tokens, status_code=status.HTTP_200_OK,
    description="Авторизация пользователя через провайдера "
                "(vk, yandex, google)",
    tags=["Social Auth"],
)
async def oauth_auth(
        provider_name: str,
        code: str,
        social_auth_service: SocialAuthService = Depends(
            get_social_auth_service),
):
    return await social_auth_service.auth(provider_name, code)
