from addict import Dict
from elasticsearch_dsl import Document, Float, Integer, Keyword


class Basic(Document):
    title_id = Keyword()
    image_url = Keyword(index=False)
    original_title = Keyword(index=False)
    genres = Keyword()
    start_year = Integer()
    average_rating = Float()
    num_votes = Integer()
    score = Float()
    title_type = Keyword()

    class Index:
        name = 'basic'

        settings = Dict()
        settings.number_of_shards = 3
        settings.number_of_replicas = 1
