import sys
from datetime import datetime
from time import sleep
import asyncio

import psycopg2
import elasticsearch
from logger import logger
from settings import Settings
from storage.elasticsearch import ElasticSaver
from storage.postgres import PostgresConn, PostgresExtractor
from state import State, JsonFileStorage


async def start_etl():

    try:
        settings = Settings()
        dsn = {
            'dbname': settings.DB_NAME,
            'user': settings.DB_USER,
            'password': settings.DB_PASSWORD,
            'host': settings.DB_HOST,
            'port': settings.DB_PORT,
            'options': settings.DB_OPTIONS,
        }
        storage = JsonFileStorage(file_path='data.json')
        app_state = State(storage=storage)
        index_names = ('movies', 'genres', 'persons')
        for index_name in index_names:
            es_client = elasticsearch.Elasticsearch(hosts=settings.ES_URL)
            es_saver = ElasticSaver(connection=es_client, index_name=index_name)

            index_exists = es_saver.index_exists()
            if not index_exists:
                logger.info('Index not exists, creating')
                es_saver.index_create()

            with PostgresConn(db_config=dsn) as pg_conn:
                pg_extractor = PostgresExtractor(connection=pg_conn)

                upload_complete = app_state.get_state(f'{index_name} upload_complete_at')

                if not upload_complete:
                    logger.info(f'{index_name} upload not comlete')
                    upload_data_to_etl(
                        state=app_state, postgres_extractor=pg_extractor, elastic_saver=es_saver, index_name=index_name,
                    )

                logger.info(f'{index_name} upload comlete')

        while True:
            tasks = []
            try:
                for index_name in index_names:
                    pg_conn = PostgresConn(db_config=dsn)
                    es_client = elasticsearch.Elasticsearch(hosts=settings.ES_URL)
                    es_saver = ElasticSaver(connection=es_client, index_name=index_name)
                    tasks.append(find_updated_data(state=app_state,
                                                   postgres_extractor=pg_extractor,
                                                   elastic_saver=es_saver,
                                                   index_name=index_name))
                    sleep(settings.POLING_DATA_INTERVAL)

                await asyncio.gather(*tasks)

            except (psycopg2.InterfaceError, psycopg2.OperationalError, psycopg2.ProgrammingError):
                if pg_conn.db_conn:
                    pg_conn.db_conn.close()

            except Exception as exc:
                logger.info(f'!!! Something went wrong... \n\t {exc}')

    except KeyboardInterrupt:
        sys.exit()


def upload_data_to_etl(
        state: State, postgres_extractor: PostgresExtractor, elastic_saver: ElasticSaver, index_name: str,
) -> None:
    logger.info(f'start upload data {index_name}')

    last_upload_id = state.get_state(f'{index_name} upload_last_id')
    if not last_upload_id:
        logger.info('first run upload')
        state.set_state(f'{index_name} upload_started_at', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))

    upload_started_at = state.get_state(f'{index_name} upload_started_at')
    logger.info(f'{index_name} upload_started_at = {upload_started_at}')

    data = postgres_extractor.extract_table_data(
        before_date=upload_started_at, last_upload_id=last_upload_id, index_name=index_name)

    for chunk_data in data:
        result = elastic_saver.bulk_insert(chunk_data)
        logger.debug(result)
        logger.debug('===================================')

        state.set_state(f'{index_name} upload_last_id', chunk_data[-1]['id'])

    state.set_state(f'{index_name} upload_complete_at', datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))


def find_updated_data(
        state: State, postgres_extractor: PostgresExtractor, elastic_saver: ElasticSaver, index_name: str,
):
    logger.info(f'start updating {index_name} data')

    update_started_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    updated_after = state.get_state(f'{index_name} update_started_at')
    if not updated_after:
        updated_after = state.get_state(f'{index_name} upload_started_at')

    logger.debug(updated_after)

    index_name_to_func = {
        'movies': ['get_updated_film_works', 'get_updated_film_works_genre', 'get_updated_film_works_person'],
        'genres': ['get_updated_genres'],
        'persons': ['get_updated_persons'],
    }
    for method_name in index_name_to_func[index_name]:
        data = getattr(postgres_extractor, method_name)(updated_after=updated_after)
        logger.debug(method_name)
        for chunk_data in data:
            logger.debug(chunk_data)
            result = elastic_saver.bulk_insert(chunk_data)
            logger.debug(result)
        logger.debug('-------------------------------------')
    state.set_state(key=f'{index_name} update_started_at', value=update_started_at)
    yield


def main():
    asyncio.run(start_etl())


if __name__ == '__main__':
    main()
