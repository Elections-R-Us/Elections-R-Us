from sqlalchemy import (
    Column,
    Integer,
    UnicodeText,
    ForeignKey
)

from .meta import Base


class FavoriteReferendum(Base):
    __tablename__ = 'favoritereferendums'
    id = Column(Integer, primary_key=True)
    title = Column(UnicodeText)
    brief = Column(UnicodeText)
    position = Column(UnicodeText)
    userid = Column(Integer, ForeignKey('users.id'))
