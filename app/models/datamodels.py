
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    spotify_id = Column(String, unique=True)
    email = Column(String, unique=True)
    name = Column(String)
    image_url = Column(String)
    social_links = Column(JSON)  # Flexible storage for different social platforms
    created_at = Column(DateTime, default=datetime.utcnow)

class Connection(Base):
    __tablename__ = "connections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requester_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    receiver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    status = Column(Enum("pending", "accepted", "rejected", name="connection_status"))
    created_at = Column(DateTime, default=datetime.utcnow)

class MoodRoom(Base):
    __tablename__ = "mood_rooms"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    mood = Column(String)
    description = Column(String)
    current_track = Column(JSON)  # Store current track details
    created_at = Column(DateTime, default=datetime.utcnow)

class MusicProfile(Base):
    __tablename__ = "music_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    top_artists = Column(JSON)
    top_genres = Column(JSON)
    music_soul_level = Column(Integer)
    last_updated = Column(DateTime, default=datetime.utcnow)