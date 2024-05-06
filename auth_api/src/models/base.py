import uuid
from datetime import datetime
from typing import Any, Union

from sqlalchemy import Column, ForeignKey, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from werkzeug.security import check_password_hash, generate_password_hash

Base: Any = declarative_base()


class UUidMixin(object):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                unique=True, nullable=False)


class TimestampMixin(object):
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)


class User(UUidMixin, TimestampMixin, Base):
    __tablename__ = 'user'

    login = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))

    def __init__(self, login: str, email: str, password: str,
                 first_name: Union[str, None] = None,
                 last_name: Union[str, None] = None) -> None:
        self.login = login
        self.email = email
        self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __repr__(self) -> str:
        return f'<User {self.login}>'


class TokenPair(UUidMixin, TimestampMixin, Base):
    __tablename__ = 'token_pair'

    user_id = Column(UUID(as_uuid=True), nullable=False)
    jti = Column(UUID(as_uuid=True), nullable=False)
    user_agent = Column(String(255))
    logout_at = Column(DateTime)


class Role(UUidMixin, TimestampMixin, Base):
    __tablename__ = 'role'

    name = Column(String(50), nullable=False)
    description = Column(String(255), nullable=False)

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    def __repr__(self) -> str:
        return f'<Role {self.name}>'


class UserRole(UUidMixin, TimestampMixin, Base):
    __tablename__ = 'userrole'

    user_id = Column(UUID(as_uuid=True),
                     ForeignKey('user.id', ondelete='CASCADE'))
    role_id = Column(UUID(as_uuid=True),
                     ForeignKey('role.id', ondelete='CASCADE'))


class SocialAccount(UUidMixin, TimestampMixin, Base):
    __tablename__ = 'social_account'

    user_id = Column(UUID(as_uuid=True),
                     ForeignKey('user.id', ondelete='CASCADE'))
    social_id = Column(String(255))
    social_name = Column(String(255))

    def __repr__(self) -> str:
        return f'<SocialAccount {self.social_name}:{self.user_id}>'
