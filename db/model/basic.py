from attrdict import AttrDict
from db import Base
from enum import Enum
from sqlalchemy import Boolean, Column, Date, Integer, SmallInteger, String, Text
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

    @staticmethod
    def get_by_type(type='movie'):
        mapping = {
            'movie': [
                'movie',
                'tv_movie',
                'short',
                'tv_short',
                'tv_special'
            ],
            'series': [
                'tv_series',
                'tv_mini_series'
            ]
        }

        names = mapping[type]

        values = []

        for name in names:
            key = name.upper()
            values.append(TitleType[key].value)

        return values


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
    genres = Column('genres', Array(String(20)))
    description = Column('description', Text)
    image_url = Column('image_url', Text)
    horizontal_image = Column('horizontal_image', Text)
    published_date = Column('published_date', Date)
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
