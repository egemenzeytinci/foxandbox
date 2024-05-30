from addict import Dict
from db.model import TitleType
from db.service import BasicService
from elastic import es
from elastic.model import Basic
from elasticsearch import helpers
from elasticsearch_dsl import Search, Q
from util.log import logger


class ElasticBasicService:
    def __init__(self):
        self._name = 'basic'

        # minimum year of the year categories
        self._min_year_ = 1949

    def _save(self, basics):
        """
        Save data to basic index

        :param list basics: list of basic instances
        """
        # bulk insert to index
        response = helpers.bulk(es, (b.to_dict(include_meta=True) for b in basics))

        # the problem document count
        warnings = len(basics) - response[0]

        if warnings > 0:
            logger.warning(f'An error occurred for {warnings} items')

    def save_all(self):
        """
        Save data to elasticsearch index
        """
        bs = BasicService()

        offset = 0
        limit = 500

        while True:
            # get movies by timestamp with limit and offset
            results = bs.get_by_limit_and_offset(offset=offset, limit=limit)

            if len(results) == 0:
                break

            items = []

            for r in results:
                # unique title id
                meta = Dict()
                meta.id = r.basic.title_id

                # create basic instance
                b = Basic(meta=meta)

                # set features
                b.title_id = r.basic.title_id
                b.primary_title = r.basic.primary_title
                b.genres = r.basic.genres
                b.start_year = r.basic.start_year
                b.average_rating = r.rating.average_rating
                b.score = r.rating.average_rating * r.rating.num_votes
                b.num_votes = r.rating.num_votes
                b.title_type = r.basic.title_type

                items.append(b)

            self._save(items)

            offset += limit

    def search(
        self,
        genres,
        years,
        score,
        num_votes,
        page=1,
        size=12,
        type='movie',
        exact=True
    ):
        """
        Search on basic index

        :param list genres: list of genres
        :param list years: list of years e.g. ['2020s', '2010s']
        :param int page: page number
        :param int size: number of movies to return
        :param bool exact: combination of genres or one by one
        :return: list of movies and total hitted movies
        :rtype: attrdict.AttrDict
        """
        musts = []

        filters = []

        # get title types by general type (movie or series)
        title_types = TitleType.get_by_type(type)

        musts.append(Q('terms', title_type=title_types))

        # if exact match or not
        if genres and exact:
            for genre in genres:
                musts.append(Q('term', genres=genre))

        if genres and not exact:
            musts.append(Q('terms', genres=genres))

        ranges = []

        if years:
            # filter by year
            for year in years:
                lower = year - 9

                if year == self._min_year_:
                    lower = 1800

                year_filter = {
                    'gte': lower,
                    'lte': int(year)
                }

                range_query = Q('range', start_year=year_filter)

                ranges.append(range_query)

            filters.append(Q('bool', should=ranges))

        # filter by imdb score
        if score:
            score_filter = Q('range', average_rating={'gte': float(score)})
            filters.append(score_filter)

        # filter by number of votes
        if num_votes:
            vote_filter = Q('range', num_votes={'gte': num_votes})
            filters.append(vote_filter)

        # search object by limit and offset
        from_ = (page - 1) * size

        s = Search(using=es, index=self._name).extra(from_=from_, size=size)

        # sort by score (num_votes * average_rating) descending
        s = s.sort('-score')

        # set query
        s.query = Q('bool', must=musts, filter=filters)

        s = s.source()

        # execute query
        response = s.execute()

        # check timeout
        if response.timed_out:
            return None

        r = Dict()

        r.hits = [h.to_dict() for h in response.hits]
        r.total_count = response.hits.total.value

        return r
