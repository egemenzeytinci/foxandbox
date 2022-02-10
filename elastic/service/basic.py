from attrdict import AttrDict
from db.service import BasicService
from elastic import es
from elastic.model import Basic
from elasticsearch import helpers
from elasticsearch_dsl import Search, Q
from util.log import logger


class ElasticBasicService:
    def __init__(self):
        self._name = 'basic'

        self._year_map = {
            '2020s': [2020, 2029],
            '2010s': [2010, 2019],
            '2000s': [2000, 2009],
            '1990s': [1990, 1999],
            '1980s': [1980, 1989],
            '1970s': [1970, 1979],
            '1960s': [1960, 1969],
            '1950s': [1950, 1959],
            'b1950': [1800, 1949]
        }

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
            results = bs.get_by_limit_and_offset(offset=offset, limit=limit, is_home=False)

            if len(results) == 0:
                break

            items = []

            for r in results:
                # unique title id
                meta = AttrDict()
                meta.id = r.basic.title_id

                # create basic instance
                b = Basic(meta=meta)

                # set features
                b.title_id = r.basic.title_id
                b.image_url = r.basic.image_url
                b.original_title = r.basic.original_title
                b.genres = r.basic.genres
                b.start_year = r.basic.start_year
                b.average_rating = r.rating.average_rating
                b.num_votes = r.rating.num_votes
                b.title_type = r.basic.title_type

                items.append(b)

            self._save(items)

            offset += limit

    def search(self, genres, years, page=1, size=12, exact=True):
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

        # if exact match or not
        if exact:
            for genre in genres:
                musts.append(Q('term', genres=genre))
        else:
            musts.append(Q('terms', genres=genres))

        ranges = []

        for year in years:
            lower, upper = self._year_map[year]

            # filter by year
            year_filter = {
                'gte': lower,
                'lte': upper
            }

            range_query = Q('range', start_year=year_filter)

            ranges.append(range_query)

        filters = [
            Q('bool', should=ranges)
        ]

        # search object by limit and offset
        from_ = (page - 1) * size
        s = Search(using=es, index=self._name).extra(from_=from_, size=size)

        # set query
        s.query = Q('bool', must=musts, filter=filters)

        s = s.source()

        # execute query
        response = s.execute()

        # check timeout
        if response.timed_out:
            return None

        r = AttrDict()

        r.hits = [h.to_dict() for h in response.hits]
        r.total_count = response.hits.total.value

        return r
