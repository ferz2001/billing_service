from datetime import datetime
from typing import Union
from uuid import UUID

from pydantic import BaseModel, EmailStr


class SignInUser(BaseModel):
    email: EmailStr
    password: str


class SignUpUser(SignInUser):
    login: str
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None

    class Config:
        from_attributes = True


class UserInDB(BaseModel):
    id: UUID
    login: str
    email: EmailStr
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None

    class Config:
        from_attributes = True


class SignInUserResponse(BaseModel):
    access_token: str
    refresh_token: str

    id: UUID
    email: EmailStr
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    roles: list[str]


class AccessToken(BaseModel):
    access_token: Union[str, None] = None


class RefreshToken(BaseModel):
    refresh_token: str


class ChangeLogin(BaseModel):
    new_login: str


class Tokens(BaseModel):
    access_token: str
    refresh_token: str


class Roles(BaseModel):
    name: str
    description: str


class ChangePassword(BaseModel):
    new_password: str


class Session(BaseModel):
    date_login: datetime
    user_agent: Union[str, None] = None
    logout_at: Union[datetime, None] = None


class AuthorizeUrl(BaseModel):
    url: str


class SocialAccountInDb(BaseModel):
    id: UUID
    social_id: str
    social_name: str

    class Config:
        from_attributes = True
