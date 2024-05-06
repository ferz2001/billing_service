import abc
from http import HTTPStatus
from typing import Optional, List

from schemas.base import Roles


class AsyncRolesService(abc.ABC):

    @abc.abstractmethod
    async def create_role(
            self,
            name: str,
            description: str,
    ) -> Optional[Roles]:
        pass

    @abc.abstractmethod
    async def delete_role(self, name: str) -> Optional[HTTPStatus]:
        pass

    @abc.abstractmethod
    async def change_role(
            self,
            name: str,
            new_description: str,
            new_name: str,
    ) -> Optional[HTTPStatus]:
        pass

    @abc.abstractmethod
    async def get_roles(self) -> Optional[List[Roles]]:
        pass

    @abc.abstractmethod
    async def set_role_to_user(
            self,
            email: str,
            role_name: str,
    ) -> Optional[Roles]:
        pass

    @abc.abstractmethod
    async def delete_role_to_user(
            self,
            email: str,
            role_name: str,
    ) -> Optional[HTTPStatus]:
        pass
