from addict import Dict
from db import Base
from sqlalchemy import Column, Float, Integer, String


class Rating(Base):
    __tablename__ = 'ratings'

    title_id = Column('title_id', String(20), primary_key=True)
    average_rating = Column('average_rating', Float)
    num_votes = Column('num_votes', Integer)

    @staticmethod
    def mapping():
        mapping = Dict()
        mapping.tconst = 'title_id'
        mapping.averageRating = 'average_rating'
        mapping.numVotes = 'num_votes'

        return mapping
