import logging
from functools import lru_cache
from functools import wraps
from http import HTTPStatus
from typing import List, Optional, Union

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select, delete

from core.config import settings
from db.postgres import get_session, DbService
from models.base import Role, User, UserRole
from schemas.base import Roles
from services.auth import get_current_user
from .base import AsyncRolesService

logger = logging.getLogger(f'{settings.app_name}.{__name__}')


class RolesService(AsyncRolesService):
    def __init__(self, db_service: DbService) -> None:
        self.db_service = db_service
    
    async def _check_role_by_name(self, name: str) -> Union[User, None]:
        role_exist = await self.db_service.select(
            what_select=Role,
            where_select=[(Role.name, name)]
        )
        if len(role_exist) > 0:
            return role_exist[0]
        return None

    async def _check_user_by_email(self, email: str) -> Union[User, None]:
        existing_user = await self.db_service.select(
            what_select=User,
            where_select=[(User.email, email)]
        )
        if len(existing_user) > 0:
            return existing_user[0]
        return None

    async def get_user_roles(self, user: User) -> list:
        user_roles = await self.db_service.select(
            what_select=Role.name,
            where_select=[(UserRole.user_id, user.id)],
            join_with=UserRole
        )
        logger.debug('Got user roles: %s', user_roles)
        return user_roles

    async def create_role(
            self,
            name: str,
            description: str
    ) -> Union[Optional[Roles], HTTPStatus]:
        try:
            role_exist = await self._check_role_by_name(name=name)
            if role_exist is None:
                return HTTPStatus.BAD_REQUEST

            await self.db_service.insert(
                what_insert=Role,
                values_insert={
                    "name": name,
                    "description": description
                }
            )
        except Exception as err:
            logging.info(
                'Error creating role [%s]  with description [%s]', name, description
            )
            logging.info('Error creating role: %s', err)
            
            return None
        return Roles(name=name, description=description)

    async def change_role(
            self,
            name: str,
            new_description: str,
            new_name: str,
    ) -> Optional[HTTPStatus]:
        try:
            role_exist = await self._check_role_by_name(name=name)
            if role_exist is None:
                return HTTPStatus.BAD_REQUEST

            values = {"description": new_description}
            values.update({'name': new_name}) if new_name else ''
            await self.db_service.update(
                what_update=Role,
                where_update=[Role.name, name],
                values_update=values
            )
        except Exception as err:
            logging.info(
                'Error updating role [%s] to new name [%s] with description [%s]',
                name, new_name, new_description
            )
            logging.info('Updating role error: %s', err)
            return None
        return HTTPStatus.ACCEPTED

    async def get_roles(self) -> Optional[List[Roles]]:
        try:
            datas = await self.db_service.select(Role)
            return [
                Roles(name=data.name, description=data.description)
                for data in datas
            ]
        except Exception as err:
            logging.info('Error with getting all roles: %s', err)
            return None
    
    async def delete_role(self, name: str) -> Optional[HTTPStatus]:
        try:
            role_exist = await self._check_role_by_name(name=name)
            if role_exist is None:
                return HTTPStatus.BAD_REQUEST
            await self.db_service.delete(
                what_delete=Role,
                where_delete=[(Role.name, name)]
            )
            return HTTPStatus.ACCEPTED
        except Exception as err:
            logging.info('Error deleting role [%s]: %s', name)
            logging.info('Reason: %s', err)
            return None
    
    async def set_role_to_user(
            self,
            email: str,
            role_name: str,
    ) -> Union[Optional[List[Roles]], HTTPStatus]:
        
        role_exist = await self._check_role_by_name(name=role_name)
        if role_exist is None:
            return HTTPStatus.BAD_REQUEST
        existing_user = await self._check_user_by_email(email=email)
        if existing_user is None:
            return HTTPStatus.CONFLICT
        
        user_roles = await self.db_service.db.execute(
            select(UserRole)
            .where(
                UserRole.user_id == existing_user.id,
                UserRole.role_id == role_exist.id
            )
        )
        if user_roles.scalar():
            user_roles = await self.db_service.select(
                what_select=Role,
                where_select=[(UserRole.user_id, existing_user.id)],
                join_with=UserRole
            )
            return [
                Roles(name=role.name, description=role.description)
                for role in user_roles
            ]
        
        data_insert = UserRole(
            user_id=existing_user.id,
            role_id=role_exist.id
        )
        
        await self.db_service.insert_data(data_insert)
        user_roles = await self.db_service.select(
            what_select=Role,
            where_select=[(UserRole.user_id, existing_user.id)],
            join_with=UserRole
        )
        return [
            Roles(name=role.name, description=role.description)
            for role in user_roles
        ]
    
    async def delete_role_to_user(
            self,
            email: str,
            role_name: str,
    ) -> Optional[HTTPStatus]:
        try:
            role_exist = await self._check_role_by_name(name=role_name)
            if role_exist is None:
                return HTTPStatus.BAD_REQUEST
            existing_user = await self._check_user_by_email(email=email)
            if existing_user is None:
                return HTTPStatus.CONFLICT
            
            await self.db_service.db.execute(
                delete(UserRole)
                .where(
                    UserRole.user_id == existing_user.id,
                    UserRole.role_id == role_exist.id,
                )
            )
            await self.db_service.db.commit()
            return HTTPStatus.OK
        except Exception as err:
            logger.info('Error deleting role [%s] to user [%s]', role_name, email)
            logger.info('Reason: %s', err)
            return None
    
    async def check_permission(self, user: User, role: str):
        if role not in await self.get_user_roles(user):
            logger.info(
                'Role %s does not exist in user [%s] role list',
                role, user.email
            )
            raise HTTPException(403, 'Вы не являетесь админом.')


def check_admin_permission(func):
    @wraps(func)
    async def wrapper(
            *args,
            user: User = Depends(get_current_user),
            role_service: RolesService = Depends(role_services),
            **kwargs):
        await role_service.check_permission(user, 'admin')
        return await func(*args, user=user, role_service=role_service,
                          **kwargs)
    
    return wrapper


@lru_cache()
def role_services(
        db: AsyncSession = Depends(get_session),
) -> RolesService:
    return RolesService(
        db_service=DbService(db=db),
    )
