from db import get_session
from db.model import Rating


class RatingService:
    def get_by_offset(self, limit=500, offset=0):
        """
        Get rating objects by page

        :param int limit: limit
        :param int offset: offset
        :return: rating objects
        :rtype: list[Rating]
        """
        session = get_session()

        # order by popularity
        order = (Rating.num_votes * Rating.average_rating).desc()

        try:
            return session \
                .query(Rating) \
                .order_by(order) \
                .limit(limit) \
                .offset(offset * limit) \
                .all()
        finally:
            session.close()
