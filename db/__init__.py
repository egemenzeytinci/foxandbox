from sqlalchemy import create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from util.config import config


def get_engine():
    """
    Get SQLAlchemy engine by using parameters

    :return: SQLAlchemy engine
    :rtype: sqlalchemy.engine.Engine
    """
    host = config.db.host
    port = config.db.port
    user = config.db.user
    password = config.db.password
    db = config.db.db

    u = f'postgresql://{user}:{password}@{host}:{port}/{db}'

    return create_engine(u)


def get_session():
    """
    Returns SQLAlchemy session

    :return: session
    :rtype: sqlalchemy.orm.session.Session
    """
    return SessionItem()


# get default engine from db configuration
engine = get_engine()

insp = inspect(engine)

Base = declarative_base()
SessionItem = sessionmaker(bind=engine, autocommit=False)
