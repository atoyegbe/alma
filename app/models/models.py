from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, ARRAY, String, JSON, DateTime

class User(SQLModel, table=True):
    __tablename__ = "users"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    spotify_id: Optional[str] = Field(unique=True, default=None)
    spotify_token: Optional[str] = Field(default=None)
    spotify_refresh_token: Optional[str] = Field(default=None)
    token_expires_at: Optional[datetime] = Field(default=None)
    
    # Profile Information
    display_name: Optional[str] = Field(default=None)
    spotify_url: Optional[str] = Field(default=None)
    spotify_image_url: Optional[str] = Field(default=None)
    country: Optional[str] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_spotify_sync: Optional[datetime] = Field(default=None)
    
    # Relationships
    music_profile: Optional["MusicProfile"] = Relationship(back_populates="user")
    connections: List["Connection"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "Connection.user_id"}
    )
    mood_rooms: List["MoodRoom"] = Relationship(back_populates="owner")
    playlists: List["Playlist"] = Relationship(back_populates="user")


class MusicProfile(SQLModel, table=True):
    __tablename__ = "music_profiles"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", unique=True)
    
    # Music Taste Information
    top_artists: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
    top_tracks: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
    genres: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
    
    # Extended Music Profile Data
    favorite_decades: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
    preferred_genres: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
    discovery_preferences: Optional[Dict] = Field(default=None, sa_column=Column(JSON))
    listening_history: Optional[Dict] = Field(default=None, sa_column=Column(JSON))
    
    # Metrics and Analysis
    energy_score: Optional[float] = Field(default=None)
    danceability_score: Optional[float] = Field(default=None)
    diversity_score: Optional[float] = Field(default=None)
    obscurity_score: Optional[float] = Field(default=None)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="music_profile")


class Connection(SQLModel, table=True):
    __tablename__ = "connections"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    connected_user_id: UUID = Field(foreign_key="users.id")
    status: str
    overall_compatibility: Optional[int] = Field(default=None)
    compatibility_breakdown: Optional[Dict] = Field(default=None, sa_column=Column(JSON))
    shared_genres: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
    shared_artists: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
    shared_tracks: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="connections", sa_relationship_kwargs={"foreign_keys": "[Connection.user_id]"})
    connected_user: User = Relationship(sa_relationship_kwargs={"foreign_keys": "[Connection.connected_user_id]"})

class MoodRoom(SQLModel, table=True):
    __tablename__ = "mood_rooms"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    owner_id: UUID = Field(foreign_key="users.id")
    name: str
    description: Optional[str] = Field(default=None)
    mood_tags: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
    playlist_id: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    owner: User = Relationship(back_populates="mood_rooms")


class Playlist(SQLModel, table=True):
    __tablename__ = "playlists"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    name: str
    description: Optional[str] = None
    public: bool = True
    spotify_id: str = Field(unique=True, index=True)
    tracks: List[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime, onupdate=datetime.utcnow)
    )

    user: Optional["User"] = Relationship(back_populates="playlists")

    def to_response(self) -> Dict[str, Any]:
        """Convert to response format matching Spotify's playlist format"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "public": self.public,
            "tracks": {"items": self.tracks},
            "owner": {"id": str(self.user_id)},
            "spotify_id": self.spotify_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
