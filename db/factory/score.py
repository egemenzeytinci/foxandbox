from db import get_session
from db.model import Basic, Rating


class ScoreFactory:
    def get_all(self):
        """
        Get features about the scoring

        :return: list of ratings and basics features
        :rtype: list
        """
        session = get_session()

        columns = [
            Basic.title_id,
            Basic.start_year,
            Basic.title_type,
            Basic.runtime,
            Rating.num_votes,
        ]

        filters = [
            Basic.is_crawled.is_(True),
            Basic.runtime.isnot(None),
        ]

        try:
            return session.query(*columns) \
                .join(Rating, Rating.title_id == Basic.title_id) \
                .filter(*filters) \
                .all()
        finally:
            session.close()
