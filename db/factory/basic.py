from db import get_session
from db.model import Basic


class BasicFactory:
    def get_by_ids(self, ids):
        """
        Get basic objects by page

        :param list ids: title ids
        :return: basic objects
        :rtype: list[Basic]
        """
        session = get_session()

        try:
            return session.query(Basic).filter(Basic.title_id.in_(ids)).all()
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
