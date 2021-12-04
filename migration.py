from db import engine, insp
from db.model import Basic, Episode, Rating
from termcolor import colored
from util.config import config
from util.log import logger

if __name__ == '__main__':
    tables = [
        Basic,
        Episode,
        Rating,
    ]

    for table in tables:
        table_name = table.__tablename__

        tc = colored(table_name, 'green', attrs=['bold'])

        if insp.has_table(table_name, schema=config.db.schema):
            logger.info(tc + ' table is already exist')
            continue

        logger.info(tc + ' table is creating')

        try:
            table.__table__.create(engine)
        except Exception as e:
            m = tc + ' table could not created. Please check bellow.'
            logger.error(m)
            logger.exception(e)
