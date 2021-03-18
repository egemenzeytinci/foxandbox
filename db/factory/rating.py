from db import get_session
from db.model import Rating


class RatingFactory:
    def get_by_offset(self, limit=500, offset=1):
        """
        Get rating objects by page

        :param int limit: limit
        :param int offset: offset
        :return: rating objects
        :rtype: list[Rating]
        """
        session = get_session()

        try:
            return session \
                .query(Rating) \
                .order_by(Rating.title_id) \
                .limit(limit) \
                .offset(offset * limit) \
                .all()
        finally:
            session.close()
