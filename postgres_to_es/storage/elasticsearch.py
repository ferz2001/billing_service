from typing import Dict
from typing import List

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from utils import backoff
from storage.elasticsearch_index_schema import MOVIES_INDEX_SCHEMA, PERSONS_INDEX_SCHEMA, GENRES_INDEX_SCHEMA


class ElasticSaver:
    movies_schema = MOVIES_INDEX_SCHEMA
    person_schema = PERSONS_INDEX_SCHEMA
    genres_schema = GENRES_INDEX_SCHEMA

    def __init__(self, connection: Elasticsearch, index_name: str) -> None:
        self.conn = connection
        self.index_name = index_name

    @backoff()
    def bulk_insert(self, data: List[Dict]) -> tuple:
        return bulk(self.conn, data, index=self.index_name)

    def index_exists(self):
        return self.conn.indices.exists(index=self.index_name)

    def index_create(self):
        if self.index_name == "movies":
            return self.conn.indices.create(index=self.index_name, body=self.movies_schema)
        elif self.index_name == "genres":
            return self.conn.indices.create(index=self.index_name, body=self.genres_schema)
        else:
            return self.conn.indices.create(index=self.index_name, body=self.person_schema)
