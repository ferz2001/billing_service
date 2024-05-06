from typing import Union

from fastapi import APIRouter, Depends, Query

from models.film import Person
from services.base import get_redis_elastic_service, FilmService
from .all_models import object_details

router = APIRouter()


@router.get('/search',
            summary="Get list Person details by query",
            description="Get list id, full_name by query",
            response_model=list[Union[Person, None]])
async def films_details(
        query: str,
        page_size: int = Query(25, alias="page[size]"),
        page_number: int = Query(1, alias="page[number]"),
        film_service: FilmService = Depends(get_redis_elastic_service)) -> list[Union[Person, None]]:
    persons = await film_service.get_obj_data_by_query(
        query=query, page_size=page_size, page_number=page_number, elastic_index_name="persons")
    return persons


@router.get('/{person_id}',
            summary="Get Person detail by id",
            description="Get id, full_name by person_id",
            response_model=Union[Person, None])
async def film_details(person_id: str, film_service: FilmService = Depends(get_redis_elastic_service)) -> Person:
    person = await film_service.get_obj_data_by_id(obj_id=person_id, elastic_index_name="persons")
    return await object_details(person)
