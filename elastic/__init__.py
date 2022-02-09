from elasticsearch import Elasticsearch
from util.config import config

es = Elasticsearch(
    hosts=config.elastic.hosts,
    port=config.elastic.port,
    retry_on_timeout=True
)
