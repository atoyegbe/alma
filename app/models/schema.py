from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel

# User Schemas
class UserBase(BaseModel):
    spotify_id: Optional[str] = None
    email: str
    name: str
    image_url: Optional[str] = None
    social_links: Optional[Dict[str, Any]] = None

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Connection Schemas
class ConnectionBase(BaseModel):
    requester_id: UUID
    receiver_id: UUID
    status: str

class ConnectionCreate(ConnectionBase):
    pass

class ConnectionResponse(ConnectionBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# MoodRoom Schemas
class MoodRoomBase(BaseModel):
    name: str
    mood: str
    description: Optional[str] = None
    current_track: Optional[Dict[str, Any]] = None

class MoodRoomCreate(MoodRoomBase):
    pass

class MoodRoomResponse(MoodRoomBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# MusicProfile Schemas
class MusicProfileBase(BaseModel):
    user_id: UUID
    top_artists: List[Dict[str, Any]]
    top_genres: List[str]
    music_soul_level: int

class MusicProfileCreate(MusicProfileBase):
    pass

class MusicProfileResponse(MusicProfileBase):
    id: UUID
    last_updated: datetime

    class Config:
        from_attributes = True

# Playlist Schemas
class PlaylistBase(BaseModel):
    name: str
    description: Optional[str] = None
    public: bool = True
    tracks: List[Dict[str, Any]] = []

class PlaylistCreate(PlaylistBase):
    pass

class PlaylistUpdate(PlaylistBase):
    pass

class PlaylistResponse(PlaylistBase):
    id: UUID
    owner_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True
