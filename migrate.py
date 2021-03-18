from db import engine
from db.model import Basic, Episode, Rating

if __name__ == '__main__':
    tables = [
        Basic,
        Episode,
        Rating,
    ]

    for table in tables:
        if engine.dialect.has_table(engine, table.__tablename__):
            continue

        table.__table__.create(engine)
