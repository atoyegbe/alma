from sqlalchemy import  Column, ForeignKey, Table, String, DateTime, UniqueConstraint, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
# from sqlalchemy.dialects.postgresql import ARRAY

from .database import Base


user_friends = Table(
    'user_friends', 
    Base.metadata,
    Column('user_id', String, ForeignKey('users.user_id'), primary_key=True),
    Column('friend_id', String, ForeignKey('users.user_id'), primary_key=True),
    # Enforce uniqueness on user_id and friend_id pairs
    UniqueConstraint('user_id', 'friend_id')
)

class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True)
    username = Column(String, unique=True, index=True)
    country = Column(String)
    geners = Column(ARRAY(String))
    top_artists = Column(ARRAY(String))
    top_albums = Column(ARRAY(String))
    created_at = Column(DateTime, default=func.now())

    friends = relationship(
        "User",
        secondary=user_friends,
        primaryjoin=id==user_friends.c.user_id,
        secondaryjoin=id==user_friends.c.friend_id,
        back_populates="friend_of",
        doc="Many-to-many relationship representing the user's friends."
    )

    # Back-populates relationship for bidirectional traversal
    friend_of = relationship(
        "User",
        secondary=user_friends,
        primaryjoin=id==user_friends.c.friend_id,
        secondaryjoin=id==user_friends.c.user_id,
        back_populates="friends"
    )
