from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    UnicodeText,
    ForeignKey
)

from .user import User

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
    user = relationship("User", back_populates="favoritecandidates")

User.favoritecandidates = relationship(
    'FavoriteCandidate', order_by=FavoriteCandidate.id, back_populates='user'
)
