from addict import Dict
from db import get_session
from db.model import Basic, ImageStatus, Rating, TitleType
from sqlalchemy import cast, func, String
from sqlalchemy.dialects.postgresql import array, ARRAY


class BasicService:
    def get_by_id(self, title_id):
        """
        Get basic object by given id

        :param str title_id: title id
        :return: basic object
        :rtype: attrdict.AttrDict
        """
        session = get_session()

        b = Basic
        r = Rating

        try:
            row = session \
                .query(b, r) \
                .join(r, b.title_id == r.title_id) \
                .filter(b.title_id == title_id) \
                .first()

            if not row:
                return None

            result = Dict()

            result.basic = row[0]
            result.rating = row[1]

            return result
        finally:
            session.close()

    def get_by_ids(self, ids):
        """
        Get basic objects by page

        :param list ids: title ids
        :return: basic objects
        :rtype: list[Basic]
        """
        session = get_session()

        filters = [
            Basic.title_id.in_(ids),
            Basic.is_crawled.is_(False),
        ]

        try:
            return session.query(Basic).filter(*filters).all()
        finally:
            session.close()

    def get_most_popular_items(
        self,
        offset=0,
        limit=10,
        type='movie',
        img_status=ImageStatus.BOTH
    ):
        """
        Get items by type (movie or series)

        :param int offset: offset
        :param int limit: limit
        :param str type: movie or series
        :return: list of movies
        :rtype: list[Basic, Rating]
        """
        b = Basic
        r = Rating

        session = get_session()

        title_types = TitleType.get_by_type(type)

        filters = [
            b.description.isnot(None),
            b.image_status == img_status,
            b.title_type.in_(title_types),
        ]

        try:
            rows = session \
                .query(b, r) \
                .join(r, b.title_id == r.title_id) \
                .filter(*filters) \
                .order_by((r.num_votes * r.average_rating).desc()) \
                .offset(offset * limit) \
                .limit(limit) \
                .all()

            results = []

            for row in rows:
                a = Dict()
                a.basic = row[0]
                a.rating = row[1]

                results.append(a)

            return results
        finally:
            session.close()

    def get_by_limit_and_offset(self, offset=0, limit=10):
        """
        Get movies by limit and offset

        :param int offset: offset
        :param int limit: limit
        :return: list of movies
        :rtype: list[Basic, Rating]
        """
        b = Basic
        r = Rating

        session = get_session()

        filters = [
            b.description.isnot(None),
            b.image_status >= ImageStatus.VERTICAL_IMAGE,
        ]

        try:
            rows = session \
                .query(b, r) \
                .join(r, b.title_id == r.title_id) \
                .filter(*filters) \
                .order_by(b.title_id) \
                .offset(offset) \
                .limit(limit) \
                .all()

            results = []

            for row in rows:
                a = Dict()
                a.basic = row[0]
                a.rating = row[1]

                results.append(a)

            return results
        finally:
            session.close()

    def get_by_random(self, image_status=ImageStatus.BOTH):
        """
        Get movie by random

        :return: random movie
        :rtype: attrdict.AttrDict
        """
        session = get_session()

        b = Basic
        r = Rating

        filters = [
            r.num_votes >= 10000,
            r.average_rating >= 6.0,
            b.description.isnot(None),
            b.image_status == image_status,
            b.published_date.isnot(None),
        ]

        try:
            row = session \
                .query(b, r) \
                .join(r, b.title_id == r.title_id) \
                .filter(*filters) \
                .order_by(func.random()) \
                .first()

            a = Dict()
            a.basic = row[0]
            a.rating = row[1]

            return a
        finally:
            session.close()

    def get_new_released_movies(self):
        """
        Get new relased movies

        :return: list of movies
        :rtype: list[Basic, Rating]
        """
        b = Basic
        r = Rating
        tt = TitleType

        session = get_session()

        filters = [
            r.num_votes >= 20000,
            r.average_rating >= 6.0,
            b.description.isnot(None),
            b.image_status == ImageStatus.VERTICAL_IMAGE,
            b.title_type == tt.get('movie'),
            b.published_date.isnot(None),
        ]

        try:
            rows = session \
                .query(b, r) \
                .join(r, b.title_id == r.title_id) \
                .filter(*filters) \
                .order_by(b.published_date.desc()) \
                .limit(8) \
                .all()

            results = []

            for row in rows:
                a = Dict()
                a.basic = row[0]
                a.rating = row[1]

                results.append(a)

            return results
        finally:
            session.close()

    def get_recommendations(self, title_id, title_type, cluster, genre, limit=12):
        """
        Get recommendations by given id and title type

        :param str title_id: title id
        :param int title_type: title type movie, series, etc.
        :param int cluster: movie recommendation cluster
        :return: list of movies
        :rtype: list[Basic, Rating]
        """
        b = Basic
        r = Rating

        session = get_session()

        filters = [
            b.title_id != title_id,
            b.title_type == title_type,
            b.cluster == cluster,
        ]

        popularity = Rating.num_votes * Rating.average_rating
        similarity = func.smlar(cast(array(genre), ARRAY(String)), b.genres)

        order = [
            similarity.desc(),
            popularity.desc(),
        ]

        try:
            rows = session \
                .query(b, r) \
                .join(r, b.title_id == r.title_id) \
                .filter(*filters) \
                .order_by(*order) \
                .limit(limit) \
                .all()

            results = []

            for row in rows:
                a = Dict()
                a.basic = row[0]
                a.rating = row[1]

                results.append(a)

            return results
        finally:
            session.close()

    def get_genres(self):
        """
        Get all genres

        :return: list of genres
        :rtype: list
        """
        session = get_session()

        column = func.distinct(func.unnest(Basic.genres)).label('genre')

        try:
            return session \
                .query(column) \
                .order_by(column) \
                .all()
        finally:
            session.close()

    def save_all(self, basics):
        """
        Save all objects

        :param list[Basic] basic: basic objects
        """
        session = get_session()

        try:
            for basic in basics:
                session.merge(basic)
            session.commit()
        finally:
            session.close()
