from sqlalchemy import (
    Column,
    Integer,
    UnicodeText,
    ForeignKey
)

from .meta import Base


class FavoriteCandidate(Base):
    __tablename__ = 'favoritecandidates'
    id = Column(Integer, primary_key=True)
    candidatename = Column(UnicodeText)
    office = Column(UnicodeText)
    userid = Column(Integer, ForeignKey('users.id'))
