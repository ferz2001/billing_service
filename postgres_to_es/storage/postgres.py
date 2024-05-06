from typing import Dict, Any
from typing import Union
from types import TracebackType
from collections.abc import Iterator

from logger import logger
import psycopg2
from psycopg2.extras import DictCursor
from utils import backoff


class PostgresConn:
    def __init__(self, db_config: Dict):
        self.db_conn: Any = None
        self.db_config = db_config

    @backoff()
    def __enter__(self) -> psycopg2.extensions.connection:
        logger.info('trying connection to postgress')
        self.db_conn = psycopg2.connect(**self.db_config, cursor_factory=DictCursor)
        logger.info('connection success')
        return self.db_conn

    def __exit__(self, exception_type: Union[BaseException, None], exception_value: Union[BaseException, None],
                 traceback: Union[TracebackType, None]) -> None:
        if self.db_conn:
            self.db_conn.close()


class PostgresExtractor:
    SQL_MOVIES = '''
        SELECT
            "content"."film_work"."id",
            "content"."film_work"."id" AS "_id",
            "content"."film_work"."rating" AS "imdb_rating",
            "content"."film_work"."title",
            COALESCE(
                "content"."film_work"."description",
                ''
            ) AS "description",

            COALESCE (
                ARRAY_AGG( DISTINCT "content"."genre"."name" ),
                '{}'
            ) AS "genre",

            COALESCE(
                ARRAY_AGG( DISTINCT "content"."person"."full_name") 
                FILTER (WHERE "content"."person_film_work"."role" = 'director'),
                '{}'
            ) AS "director",

            COALESCE(
                ARRAY_AGG( DISTINCT "content"."person"."full_name") 
                FILTER (WHERE "content"."person_film_work"."role" = 'actor'),
                '{}'
            ) AS "actors_names",

            COALESCE(
                ARRAY_AGG( DISTINCT "content"."person"."full_name") 
                FILTER (WHERE "content"."person_film_work"."role" = 'writer'),
                '{}'
            ) AS "writers_names",

            COALESCE (
                JSONB_AGG(
                    DISTINCT jsonb_build_object(
                        'id', "content"."person"."id",
                        'name', "content"."person"."full_name"
                    )
                ) FILTER (WHERE "content"."person_film_work"."role" = 'actor'),
                '[]'
            ) AS "actors",

            COALESCE (
                JSONB_AGG(
                    DISTINCT jsonb_build_object(
                        'id', "content"."person"."id",
                        'name', "content"."person"."full_name"
                    )
                ) FILTER (WHERE "content"."person_film_work"."role" = 'writer'),
                '[]'
            ) AS "writers"

        FROM "content"."film_work"
        LEFT OUTER JOIN "content"."genre_film_work" 
            ON ("content"."film_work"."id" = "content"."genre_film_work"."film_work_id")
        LEFT OUTER JOIN "content"."genre" 
            ON ("content"."genre_film_work"."genre_id" = "content"."genre"."id")
        LEFT OUTER JOIN "content"."person_film_work" 
            ON ("content"."film_work"."id" = "content"."person_film_work"."film_work_id")
        LEFT OUTER JOIN "content"."person" 
            ON ("content"."person_film_work"."person_id" = "content"."person"."id")
    '''
    SQL_GENRES = '''
        SELECT 
            "content"."genre"."id", 
            "content"."genre"."id" AS "_id", 
            "content"."genre"."name", 
            "content"."genre"."description"  
        FROM "content"."genre"
    '''
    SQL_PERSONS = '''
        SELECT "content"."person"."id", "content"."person"."id" AS "_id", "content"."person"."full_name" 
        FROM "content"."person"
    '''

    def __init__(self, connection: psycopg2.extensions.connection, chunk_size: int = 100) -> None:
        self.conn = connection
        self.chunk_size = chunk_size

    @backoff()
    def _fetch_chunked(self, sql: str, params: Union[tuple, None] = None) -> Iterator:
        if self.conn:
            with self.conn.cursor() as cur:
                cur.execute(sql, params)
                while True:
                    chunk = cur.fetchmany(self.chunk_size)
                    if not chunk:
                        break
                    yield chunk

    def extract_table_data(self, index_name: str, before_date: str,
                           last_upload_id: Union[str, None] = None) -> Iterator:
        params = [before_date]
        if index_name == 'movies':
            sql = self.SQL_MOVIES + 'WHERE "content"."film_work"."modified" <= %s'
        elif index_name == 'genres':
            sql = self.SQL_GENRES + 'WHERE "content"."genre"."modified" <= %s'
        else:
            sql = self.SQL_PERSONS + 'WHERE "content"."person"."modified" <= %s'

        if last_upload_id:
            params += [last_upload_id]
            if index_name == 'movies':
                sql += 'AND "content"."film_work"."id" > %s'
            elif index_name == 'genres':
                sql += 'AND "content"."genre"."id" > %s'
            else:
                sql += 'AND "content"."person"."id" > %s'

        if index_name == 'movies':
            sql += ' GROUP BY "content"."film_work"."id" ORDER BY "content"."film_work"."id" ASC;'
        elif index_name == 'genres':
            sql += ' GROUP BY "content"."genre"."id" ORDER BY "content"."genre"."id" ASC;'
        else:
            sql += ' GROUP BY "content"."person"."id" ORDER BY "content"."person"."id" ASC;'
        logger.info(sql)
        return self._fetch_chunked(sql=sql, params=tuple(params))

    def get_updated_film_works(self, updated_after: str) -> Iterator:
        sql = self.SQL_MOVIES + (
            'WHERE "content"."film_work"."id" IN ('
            'SELECT film_work.id'
            'FROM film_work'
            'WHERE modified > %s)'
        )
        sql += ' GROUP BY "content"."film_work"."id" ORDER BY "content"."film_work"."id" ASC;'

        return self._fetch_chunked(sql=sql, params=(updated_after,))

    def get_updated_film_works_person(self, updated_after: str) -> Iterator:
        sql = self.SQL_MOVIES + (
            'WHERE "content"."film_work"."id" IN ('
            'SELECT film_work.id'
            'FROM person'
            'LEFT JOIN person_film_work ON person_film_work.person_id = person.id'
            'LEFT JOIN film_work ON film_work.id = person_film_work.film_work_id'
            'WHERE person.modified > %s)'
        )
        sql += ' GROUP BY "content"."film_work"."id" ORDER BY "content"."film_work"."id" ASC;'

        return self._fetch_chunked(sql=sql, params=(updated_after,))

    def get_updated_film_works_genre(self, updated_after: str) -> Iterator:
        sql = self.SQL_MOVIES + (
            'WHERE "content"."film_work"."id" IN ('
            'SELECT film_work.id'
            'FROM genre'
            'LEFT JOIN genre_film_work ON genre_film_work.genre_id = genre.id'
            'LEFT JOIN film_work ON film_work.id = genre_film_work.film_work_id'
            'WHERE genre.modified > %s)'
        )
        sql += ' GROUP BY "content"."film_work"."id" ORDER BY "content"."film_work"."id" ASC;'

        return self._fetch_chunked(sql=sql, params=(updated_after,))

    def get_updated_genres(self, updated_after: str) -> Iterator:
        sql = self.SQL_GENRES + 'WHERE "content"."genre"."modified" > %s'
        sql += 'ORDER BY "content"."genre"."id" ASC;'

        return self._fetch_chunked(sql=sql, params=(updated_after,))

    def get_updated_persons(self, updated_after: str) -> Iterator:
        sql = self.SQL_GENRES + 'WHERE "content"."person"."modified" > %s'
        sql += 'ORDER BY "content"."person"."id" ASC;'
        return self._fetch_chunked(sql=sql, params=(updated_after,))
