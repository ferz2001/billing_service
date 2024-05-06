import logging

from fastapi import APIRouter, Depends, status

from core.config import settings
from models.base import User
from schemas.base import ChangeLogin, ChangePassword, Session, \
    UserInDB
from services.accounts import AbstractAccountService, get_account_service
from services.auth import get_current_user, oauth2_scheme

router = APIRouter()

logger = logging.getLogger(f'{settings.app_name}.{__name__}')


@router.post('/logout_me', status_code=status.HTTP_200_OK, description="Выход",
             tags=["Аккаунт"])
async def logout(token=Depends(oauth2_scheme),
                 account_service: AbstractAccountService = Depends(
                     get_account_service)):
    """
    Выход пользователя.

    :param access_token: Access Token пользователя.
    :param account_service: Сервис управления аккаунтом.
    """
        
    await account_service.logout(token)


@router.post('/logout_all_devices', status_code=status.HTTP_200_OK,
             description="Выход со всех аккаунтов",
             tags=["Аккаунт"])
async def logout_all(user: User = Depends(get_current_user),
                     account_service: AbstractAccountService = Depends(
                         get_account_service)):
    """
    Выход пользователя со всех устройств.

    :param access_token: Access Token пользователя.
    :param account_service: Сервис управления аккаунтом.
    """
    await account_service.logout_all(user)


@router.put('/change_login',
            status_code=status.HTTP_200_OK,
            response_model=UserInDB,
            description="Смена логина",
            tags=["Аккаунт"])
async def change_login(change_login_data: ChangeLogin,
                       user: User = Depends(get_current_user),
                       account_service: AbstractAccountService = Depends(
                           get_account_service)) -> UserInDB:
    """
    Смена логина пользователя.

    :param change_login_data: Данные для смены логина.
    :param account_service: Сервис управления аккаунтом.
    :return: Access Token с обновленным логином.
    """
    logger.info('Request to change login for user [%s]', user.email)
    user = await account_service.change_login(user, change_login_data)
    return user


@router.put('/change_password',
            status_code=status.HTTP_200_OK,
            response_model=UserInDB,
            description="Смена пароля",
            tags=["Аккаунт"])
async def change_password(
        change_password_data: ChangePassword,
        user: User = Depends(get_current_user),
        account_service: AbstractAccountService = Depends(
            get_account_service)) -> UserInDB:
    """
    Смена пароля пользователя.

    :param change_password_data: Данные для смены пароля.
    :param account_service: Сервис управления аккаунтом.
    """
    logger.info('Request to change password for user [%s] with new pass [%s]',
                user.email, change_password_data.password)
    user = await account_service.change_password(user, change_password_data)
    return user


@router.post('/login_history',
             status_code=status.HTTP_200_OK,
             response_model=list[Session],
             description="История входов",
             tags=["Аккаунт"])
async def logins_history(
        page: int,
        user: User = Depends(get_current_user),
        account_service: AbstractAccountService = Depends(
            get_account_service)) -> list[Session]:
    """
    Получение истории входов пользователя.

    :param page: Номер страницы (пагинация).
    :param user: Запрос на текущего пользователя.
    :param account_service: Сервис управления аккаунтом.
    :return: Список сессий пользователя (Max 10) от новых к последним.
    """
    logger.info('Requst login history for user [%s] with page size [%d]',
                user.email, page)
    return await account_service.logins_history(user, page)
