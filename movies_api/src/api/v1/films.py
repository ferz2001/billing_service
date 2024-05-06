from typing import Union

from fastapi import APIRouter, Depends, Query, Request

from models.film import Film
from services.base import get_redis_elastic_service, FilmService
from .all_models import object_details
from utils.auth_check import auth_required

router = APIRouter()


@router.get('/search',
            summary="Get list Film details by query",
            description="Get list id, title, description by query",
            response_model=list[Union[Film, None]])
async def films_details(
        query: str,
        page_size: int = Query(25, alias="page[size]"),
        page_number: int = Query(1, alias="page[number]"),
        film_service: FilmService = Depends(get_redis_elastic_service)) -> list[Union[Film, None]]:
    films = await film_service.get_obj_data_by_query(
        query=query, page_size=page_size, page_number=page_number, elastic_index_name="movies")
    return films


@router.get('/{film_id}',
            summary="Get Film detail by id",
            description="Get id, title, description by film_id",
            response_model=Union[Film, None])
@auth_required
async def film_details(
        film_id: str,
        request: Request,
        film_service: FilmService = Depends(get_redis_elastic_service),
) -> Film:
    film = await film_service.get_obj_data_by_id(obj_id=film_id, elastic_index_name="movies")
    return await object_details(film)
