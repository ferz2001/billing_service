import logging
from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from core.config import settings
from models.base import User
from schemas.base import Roles
from services.auth import get_current_user
from services.roles import role_services, RolesService, check_admin_permission

router = APIRouter()

logger = logging.getLogger(f'{settings.app_name}.{__name__}')


@router.post(
    "",
    response_model=Roles,
    status_code=HTTPStatus.CREATED,
    summary="Создать роль",
    tags=["Роли"],
)
@check_admin_permission
async def create_role(
        role: Roles,
        role_service: RolesService = Depends(role_services),
        user: User = Depends(get_current_user),
):
    logger.info(f"Creating role: {role} by {user.email}")
    
    role = await role_service.create_role(
        name=role.name,
        description=role.description,
    )
    if role == HTTPStatus.BAD_REQUEST:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="This role exists",
        )
    
    if not role:
        raise HTTPException(
            status_code=HTTPStatus.BAD_GATEWAY,
            detail="Can't create role",
        )
    return role


@router.put(
    "",
    status_code=HTTPStatus.ACCEPTED,
    summary="Изменить роль",
    tags=["Роли"],
)
@check_admin_permission
async def change_role(
        name: str,
        new_name: str,
        new_description: str,
        role_service: RolesService = Depends(role_services),
        user: User = Depends(get_current_user),
):
    logger.info(f"Change role {name} by {user.email}")
    
    role = await role_service.change_role(
        name=name,
        new_name=new_name,
        new_description=new_description,
    )
    if role == HTTPStatus.BAD_REQUEST:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="This role doesn't exist",
        )
    if not role:
        raise HTTPException(
            status_code=HTTPStatus.BAD_GATEWAY,
            detail="Can't change role",
        )
    return role


@router.get(
    "",
    response_model=List[Roles],
    status_code=HTTPStatus.ACCEPTED,
    summary="Получить роли",
    tags=["Роли"],
)
@check_admin_permission
async def get_roles(
        role_service: RolesService = Depends(role_services),
        user: User = Depends(get_current_user),
):
    await role_service.check_permission(user, 'admin')
    result = await role_service.get_roles()
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.BAD_GATEWAY,
            detail="Can't select roles",
        )
    return result


@router.delete(
    "",
    status_code=HTTPStatus.ACCEPTED,
    summary="Удалить роль",
    tags=["Роли"],
)
@check_admin_permission
async def delete_role(
        name: str,
        role_service: RolesService = Depends(role_services),
        user: User = Depends(get_current_user),
):
    await role_service.check_permission(user, 'admin')
    role = await role_service.delete_role(
        name=name,
    )
    if role == HTTPStatus.BAD_REQUEST:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="This role doesn't exist",
        )
    if not role:
        raise HTTPException(
            status_code=HTTPStatus.BAD_GATEWAY,
            detail="Can't delete role",
        )
    return role


@router.post(
    "/user",
    response_model=List[Roles],
    status_code=HTTPStatus.ACCEPTED,
    summary="Назначить роль пользователю",
    tags=["Роли"],
)
@check_admin_permission
async def set_role_to_user(
        email: str,
        role_name: str,
        role_service: RolesService = Depends(role_services),
        user: User = Depends(get_current_user),
):
    await role_service.check_permission(user, 'admin')
    role = await role_service.set_role_to_user(
        email=email,
        role_name=role_name,
    )
    if role == HTTPStatus.BAD_REQUEST:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Role is not exist",
        )
    if role == HTTPStatus.CONFLICT:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="User is not exist",
        )
    
    if not role:
        raise HTTPException(
            status_code=HTTPStatus.BAD_GATEWAY,
            detail="Can't set a new role",
        )
    return role


@router.delete(
    "/user",
    status_code=HTTPStatus.ACCEPTED,
    summary="Удалить роль у пользователя",
    tags=["Роли"],
)
@check_admin_permission
async def delete_role_from_user(
        email: str,
        role_name: str,
        role_service: RolesService = Depends(role_services),
        user: User = Depends(get_current_user),
):
    await role_service.check_permission(user, 'admin')
    role = await role_service.delete_role_to_user(
        email=email,
        role_name=role_name,
    )
    if role == HTTPStatus.BAD_REQUEST:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Role is not exist",
        )
    if role == HTTPStatus.CONFLICT:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="User is not exist",
        )
    if not role:
        raise HTTPException(
            status_code=HTTPStatus.BAD_GATEWAY,
            detail="Can't delete a role for user",
        )
    return role


@router.get(
    "/me",
    response_model=List[str],
    status_code=HTTPStatus.ACCEPTED,
    summary="Получить свои роли",
    tags=["Роли"],
)
async def get_my_roles(
        role_service: RolesService = Depends(role_services),
        user: User = Depends(get_current_user),
):
    result = await role_service.get_user_roles(user)
    if not result:
        raise HTTPException(
            status_code=HTTPStatus.BAD_GATEWAY,
            detail="Can't select roles",
        )
    return result
