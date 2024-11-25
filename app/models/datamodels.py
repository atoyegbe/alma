from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, JSON, Boolean, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True)
    spotify_id = Column(String, unique=True, nullable=True)
    spotify_token = Column(String, nullable=True)
    spotify_refresh_token = Column(String, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    
    # Profile Information
    display_name = Column(String, nullable=True)
    spotify_url = Column(String, nullable=True)
    spotify_image_url = Column(String, nullable=True)
    country = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_spotify_sync = Column(DateTime, nullable=True)
    
    # Relationships
    music_profile = relationship("MusicProfile", back_populates="user", uselist=False)
    connections = relationship("Connection", back_populates="user")
    mood_rooms = relationship("MoodRoom", back_populates="owner")


class MusicProfile(Base):
    __tablename__ = "music_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    
    # Music Taste Information
    top_artists = Column(ARRAY(String), nullable=True)
    top_tracks = Column(ARRAY(String), nullable=True)
    genres = Column(ARRAY(String), nullable=True)
    
    # Extended Music Profile Data
    favorite_decades = Column(ARRAY(String), nullable=True)  # e.g., ['80s', '90s']
    preferred_genres = Column(ARRAY(String), nullable=True)  # User-selected genres
    discovery_preferences = Column(JSON, nullable=True)  # Settings for music discovery
    listening_history = Column(JSON, nullable=True)  # Recent listening patterns
    
    # Music Profile Metrics
    energy_score = Column(Integer, nullable=True)  # 0-100
    danceability_score = Column(Integer, nullable=True)  # 0-100
    diversity_score = Column(Integer, nullable=True)  # 0-100
    obscurity_score = Column(Integer, nullable=True)  # 0-100
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="music_profile")


class Connection(Base):
    __tablename__ = "connections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    connected_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    status = Column(String)  # pending, accepted, rejected
    
    # Detailed compatibility scores
    overall_compatibility = Column(Integer)  # 0-100
    compatibility_breakdown = Column(JSON)  # Stores detailed similarity scores
    
    # Shared music elements
    shared_genres = Column(ARRAY(String))
    shared_artists = Column(ARRAY(String))
    shared_tracks = Column(ARRAY(String))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="connections")
    connected_user = relationship("User", foreign_keys=[connected_user_id])


class MoodRoom(Base):
    __tablename__ = "mood_rooms"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    name = Column(String)
    description = Column(String, nullable=True)
    mood_tags = Column(ARRAY(String), nullable=True)
    playlist_id = Column(String, nullable=True)  # Spotify playlist ID
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="mood_rooms")