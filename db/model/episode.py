from addict import Dict
from db import Base
from sqlalchemy import cast, Column, ForeignKey, Integer, String
from sqlalchemy.orm import column_property


class Episode(Base):
    __tablename__ = 'episodes'

    title_id = Column('title_id', String(20), primary_key=True)
    parent_id = Column('parent_id', String(20), ForeignKey('basics.title_id'))
    season_number = Column('season_number', Integer)
    episode_number = Column('episode_number', Integer)
    info = column_property('S' + cast(season_number, String) + 'E' + cast(episode_number, String))

    @staticmethod
    def mapping():
        mapping = Dict()
        mapping.tconst = 'title_id'
        mapping.parentTconst = 'parent_id'
        mapping.seasonNumber = 'season_number'
        mapping.episodeNumber = 'episode_number'

        return mapping
