from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    UnicodeText,
    ForeignKey
)

from sqlalchemy.orm import relationship

from .meta import Base


class FavoriteCandidate(Base):
    __tablename__ = 'favoritecandidates'
    id = Column(Integer, primary_key=True)
    candidatename = Column(UnicodeText)
    party = Column(UnicodeText)
    office = Column(UnicodeText)
    website = Column(UnicodeText)
    email = Column(UnicodeText)
    phone = Column(UnicodeText)

    userid = Column(Integer, ForeignKey('users.id'))
