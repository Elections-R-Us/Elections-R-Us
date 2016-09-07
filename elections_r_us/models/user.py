from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    UnicodeText,
)

from .meta import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(UnicodeText)
    email = Column(UnicodeText)
    address = Column(UnicodeText)
    password = Column(Text)


Index('my_index', User.username, unique=True, mysql_length=255)
