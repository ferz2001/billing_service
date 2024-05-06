import logging

from fastapi import APIRouter, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm

from core.config import settings
from schemas.base import SignUpUser, UserInDB, Tokens, RefreshToken, SignInUserResponse
from services.auth import AbstractAsyncAuthService
from services.auth import get_auth_service

router = APIRouter()

logger = logging.getLogger(f'{settings.app_name}.{__name__}')


@router.post("/signup", response_model=UserInDB,
             status_code=status.HTTP_201_CREATED,
             description="Регистрация пользователя", tags=["Авторизация"])
async def signup(signup_user: SignUpUser,
                 auth_service: AbstractAsyncAuthService = Depends(
                     get_auth_service)) -> UserInDB:
    logger.info('Request signup user')
    return await auth_service.create_user(signup_user)


@router.post("/signin", response_model=SignInUserResponse, status_code=status.HTTP_200_OK,
             description="Авторизация пользователя",
             tags=["Авторизация"])
async def signin(request: Request,
                 form_data: OAuth2PasswordRequestForm = Depends(),
                 auth_service: AbstractAsyncAuthService = Depends(
                     get_auth_service)) -> Tokens:
    logger.info('Request user signin with data %s', form_data)

    return await auth_service.signin(form_data, request)


@router.post('/refresh_tokens', response_model=Tokens,
             status_code=status.HTTP_200_OK,
             description="Обновление access и refresh токенов",
             tags=["Авторизация"])
async def refresh_tokens(refresh_token: RefreshToken,
                         auth_service: AbstractAsyncAuthService = Depends(
                             get_auth_service)) -> Tokens:
    logger.info('Request user refresh token [%s]', refresh_token)
    return await auth_service.update_token_pair(refresh_token)


@router.post('/validate_token',
             status_code=status.HTTP_200_OK,
             description="Валидация access и refresh токенов",
             tags=["Авторизация"])
async def validate_token(access_token: str,
                         auth_service: AbstractAsyncAuthService = Depends(
                             get_auth_service)):
    logger.info('Request user validate token with access token [%s]', access_token)
    token_detail = await auth_service.check_token(access_token, 'access')
    return {"user_id": token_detail.get("user_id")}
