import abc
import logging
from datetime import datetime
from functools import lru_cache

from fastapi import Depends, HTTPException
from redis.client import Redis
from sqlalchemy import select, and_, update, desc
from sqlalchemy.ext.asyncio import AsyncSession
from werkzeug.security import generate_password_hash

from core.config import settings
from db.postgres import get_session, DbService
from db.redis import get_redis
from models.base import TokenPair, User
from schemas.base import Session, ChangeLogin, ChangePassword
from services.auth import AuthService

logger = logging.getLogger(f'{settings.app_name}.{__name__}')


class AbstractAccountService(AuthService, abc.ABC):
    
    @abc.abstractmethod
    async def logins_history(self, user: User, page: int) -> list[Session]:
        pass
    
    @abc.abstractmethod
    async def logout(self, access_token: str):
        pass
    
    @abc.abstractmethod
    async def logout_all(self, user: User):
        pass
    
    @abc.abstractmethod
    async def change_login(self, user: User,
                           change_login_data: ChangeLogin) -> User:
        pass
    
    @abc.abstractmethod
    async def change_password(self, user: User,
                              change_password_data: ChangePassword) -> User:
        pass


class AccountService(AbstractAccountService):
    async def get_token_pairs_with_pagination(self, user_id: str,
                                              page: int = 1,
                                              page_size: int = 10):
        """
        Получение списка пар токенов с пагинацией.

        :param user_id: Идентификатор пользователя.
        :param page: Номер страницы (пагинация).
        :param page_size: Размер страницы (количество записей на странице).
        :return: Список пар токенов пользователя с учетом пагинации.
        """
        if page <= 0:
            raise HTTPException(status_code=400,
                                detail="Номер страницы должен быть "
                                       "положительным числом и больше нуля.")
        offset = (page - 1) * page_size
        sql = select(TokenPair).filter_by(user_id=user_id).offset(
            offset).limit(page_size).order_by(desc(TokenPair.created_at))
        result = await self.db_service.db.execute(sql)
        return result.all()
    
    async def get_active_token_pairs(self, user_id: str):
        """
        Получение активных пар токенов пользователя.

        :param user_id: Идентификатор пользователя.
        :return: Список активных пар токенов пользователя.
        """
        sql = select(TokenPair).filter_by(user_id=user_id, logout_at=None)
        result = await self.db_service.db.execute(sql)
        return result.all()
    
    async def update_active_token_pairs_as_logout(self, user_id: str):
        """
        Обновление активных пар токенов пользователя как разлогиненных.

        :param user_id: Идентификатор пользователя.
        """
        logger.debug('Update active token pairs as logout for user %s', user_id)
        sql = update(TokenPair).where(
            and_(
                TokenPair.user_id == user_id,
                TokenPair.logout_at.is_(None),
            ),
        ).values(logout_at=datetime.utcnow())
        await self.db_service.db.execute(sql)
        await self.db_service.db.commit()
    
    async def logins_history(self, user: User, page: int) -> list[Session]:
        """
        Получение истории входов пользователя с пагинацией.

        :param user: Объект пользователя.
        :param page: Номер страницы (пагинация).
        :return: Список сессий пользователя с учетом пагинации.
        """
        token_pairs = await self.get_token_pairs_with_pagination(User.id, page)
        logger.debug('Got taken pairs [%s]', token_pairs)
        history = []
        for token_pair_data in token_pairs:
            token_pair: TokenPair = token_pair_data[0]
            history.append(Session(
                date_login=token_pair.created_at,
                user_agent=token_pair.user_agent,
                logout_at=token_pair.logout_at,
            ))
        if history:
            return history
        else:
            raise HTTPException(status_code=400,
                                detail="Номер страницы больше, "
                                       "чем общее количество страниц.")
    
    async def logout(self, access_token: str):
        """
        Разлогинивание пользователя по токену доступа.

        :param access_token: Токен доступа.
        """
        payload = await self.check_token(access_token, 'access')
        jti = payload['jti']
        
        logging.info('Request to logout with payload [%s]', payload)
        
        await self.set_jti_in_deny_list(jti)
        await self.db_service.update(TokenPair,
                                     {'logout_at': datetime.utcnow()},
                                     [TokenPair.jti, jti])
        
        logger.debug('Updated TokenPair with jti [%s]', str(jti))
    
    async def logout_all(self, user: User):
        """
        Разлогинивание пользователя со всех устройств.

        :param user: Пользователь, который выходит из всех аккаунтов
        """
        logger.info('Request to logout with all devices for user [%s]', user.email)
        for token_pair_data in await self.get_active_token_pairs(user.id):
            token_pair: TokenPair = token_pair_data[0]
            await self.set_jti_in_deny_list(token_pair.jti)
            await self.update_active_token_pairs_as_logout(user.id)
    
    async def change_login(self, user: User,
                           change_login_data: ChangeLogin) -> User:
        """
        Смена логина пользователя.

        :param change_login_data: Данные для смены логина.
        :param user: Пользователь, который выходит из всех аккаунтов

        :return: Новый токен доступа с обновленным логином.
        """
        await self.db_service.update(User, {
            'login': change_login_data.new_login}, [User.id, user.id])
        return await self.get_db_user_by_email(user.email)
    
    async def change_password(self, user: User,
                              change_password_data: ChangePassword) -> User:
        """
        Смена пароля пользователя.

        :param change_password_data: Данные для смены пароля.
        :return: True, если операция успешна.
        """
        hash_password = generate_password_hash(change_password_data.new_password)
        await self.db_service.update(
            User,
            {'password': hash_password},
            [User.id, user.id]
        )
        logger.debug('Change password for user [%s] successfully', user.email)
        return await self.get_db_user_by_email(user.email)


@lru_cache()
def get_account_service(
        db: AsyncSession = Depends(get_session),
        redis: Redis = Depends(get_redis),
) -> AccountService:
    """
    Получение экземпляра сервиса управления аккаунтом.

    :param db: Асинхронная сессия базы данных.
    :param redis: Клиент Redis.
    :return: Экземпляр сервиса управления аккаунтом.
    """
    return AccountService(
        db_service=DbService(db=db),
        redis=redis,
    )
