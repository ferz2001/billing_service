from typing import Union

from pydantic import BaseModel


class Base(BaseModel):
    id: str


class Film(Base):
    title: str
    description: Union[str, None] = None


class Person(Base):
    full_name: str


class Genre(Base):
    name: str
    description: Union[str, None] = None
