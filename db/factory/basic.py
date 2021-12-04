from attrdict import AttrDict
from db import get_session
from db.model import Basic, Rating, TitleType
from sqlalchemy import cast, func, String
from sqlalchemy.dialects.postgresql import array, ARRAY


class BasicFactory:
    def get_by_id(self, title_id):
        """
        Get basic object by given id

        :param str title_id: title id
        :return: basic object
        :rtype: db.model.Basic or None
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

            result = AttrDict()

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

    def get_by_limit_and_offset(self, offset=0, limit=10):
        """
        Get movies by random and day of the month

        :param int offset: offset
        :param int limit: limit
        :return: list of movies
        :rtype: list[Basic, Rating]
        """
        b = Basic
        r = Rating
        tt = TitleType

        session = get_session()

        filters = [
            r.num_votes >= 100000,
            r.average_rating >= 7.0,
            b.description.isnot(None),
            b.horizontal_image.isnot(None),
            b.title_type == tt.get('movie'),
            b.start_year > 1990,
        ]

        try:
            rows = session \
                .query(b, r) \
                .join(r, b.title_id == r.title_id) \
                .filter(*filters) \
                .order_by(b.title_id) \
                .offset(offset * limit) \
                .limit(limit) \
                .all()

            results = []

            for row in rows:
                a = AttrDict()
                a.basic = row[0]
                a.rating = row[1]

                results.append(a)

            return results
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
            b.horizontal_image.isnot(None),
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
                a = AttrDict()
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
                a = AttrDict()
                a.basic = row[0]
                a.rating = row[1]

                results.append(a)

            return results
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
