from elasticsearch import Elasticsearch
from util.config import config

es = Elasticsearch(
    hosts=config.elastic.hosts,
    port=config.elastic.port,
    http_auth=(
        config.elastic.username,
        config.elastic.password
    ),
    retry_on_timeout=True
)

