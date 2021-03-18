from attrdict import AttrDict
from db import Base
from enum import Enum
from sqlalchemy import Boolean, Column, Integer, SmallInteger, String, Text
from sqlalchemy.types import ARRAY as Array
import re


class TitleType(Enum):
    MOVIE = 1
    TV_SERIES = 2
    TV_MINI_SERIES = 3
    TV_MOVIE = 4
    SHORT = 5
    TV_SHORT = 6
    TV_SPECIAL = 7

    @staticmethod
    def get(tt):
        key = re.sub(r'(?<!^)(?=[A-Z])', '_', tt).upper()
        return TitleType[key].value


class Basic(Base):
    __tablename__ = 'basics'

    title_id = Column('title_id', String(20), primary_key=True)
    title_type = Column('title_type', SmallInteger, nullable=False, index=True)
    primary_title = Column('primary_title', String(500))
    original_title = Column('original_title', String(500))
    is_adult = Column('is_adult', Boolean)
    start_year = Column('start_year', Integer)
    end_year = Column('end_year', Integer)
    runtime = Column('runtime', Integer)
    genres = Column('genres', Array(String))
    description = Column(Text)
    image_url = Column(Text)
    cluster = Column('cluster', Integer)
    is_crawled = Column('is_crawled', Boolean, default=False, index=True)

    @staticmethod
    def mapping():
        mapping = AttrDict()
        mapping.tconst = 'title_id'
        mapping.titleType = 'title_type'
        mapping.primaryTitle = 'primary_title'
        mapping.originalTitle = 'original_title'
        mapping.isAdult = 'is_adult'
        mapping.startYear = 'start_year'
        mapping.endYear = 'end_year'
        mapping.runtimeMinutes = 'runtime'
        mapping.genres = 'genres'

        return mapping
