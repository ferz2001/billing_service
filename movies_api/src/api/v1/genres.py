from typing import Union

from fastapi import APIRouter, Depends, Query

from models.film import Genre
from services.base import get_redis_elastic_service, FilmService
from .all_models import object_details

router = APIRouter()


@router.get('/search',
            summary="Get list Genre details by query",
            description="Get list id, name, description by query",
            response_model=list[Union[Genre, None]])
async def genres_details(
        query: str,
        page_size: int = Query(25, alias="page[size]"),
        page_number: int = Query(1, alias="page[number]"),
        film_service: FilmService = Depends(get_redis_elastic_service)) -> list[Union[Genre, None]]:
    genres = await film_service.get_obj_data_by_query(
        query=query, page_size=page_size, page_number=page_number, elastic_index_name="genres")
    return genres


@router.get('/{genre_id}',
            summary="Get Genre detail by id",
            description="Get id, name, description by genre_id",
            response_model=Union[Genre, None])
async def genre_details(genre_id: str, film_service: FilmService = Depends(get_redis_elastic_service)) -> Genre:
    genre = await film_service.get_obj_data_by_id(obj_id=genre_id, elastic_index_name="genres")
    return await object_details(genre)
