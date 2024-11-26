from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field



# MusicProfile Schemas
class MusicProfileBase(BaseModel):
    """Base music profile attributes"""
    user_id: UUID
    top_artists: List[Dict[str, Any]]
    top_genres: List[str]
    music_soul_level: int

    class Config:
        orm_mode = True

class MusicProfileCreate(MusicProfileBase):
    """Attributes required to create a music profile"""
    pass

class MusicProfileUpdate(BaseModel):
    """Attributes that can be updated in a music profile"""
    top_artists: Optional[List[Dict[str, Any]]] = None
    top_genres: Optional[List[str]] = None
    music_soul_level: Optional[int] = None

class MusicProfileResponse(MusicProfileBase):
    """Full music profile response including system fields"""
    id: UUID
    last_updated: datetime
    created_at: datetime

    class Config:
        from_attributes = True
# Social Links Schema
class SocialLinks(BaseModel):
    """Pydantic model for social media links"""
    instagram: Optional[str] = Field(None, description="Instagram username")
    twitter: Optional[str] = Field(None, description="Twitter username")
    facebook: Optional[str] = Field(None, description="Facebook profile URL")
    spotify: Optional[str] = Field(None, description="Spotify profile URL")

# User Schemas
class UserBase(BaseModel):
    """Base user attributes"""
    spotify_id: str
    email: str
    name: str
    image_url: Optional[str] = None
    social_links: Optional[Dict[str, Any]] = None

    class Config:
        orm_mode = True

class UserCreate(UserBase):
    """Attributes required to create a user"""
    pass

class UserUpdate(BaseModel):
    """Attributes that can be updated"""
    name: Optional[str] = None
    image_url: Optional[str] = None
    social_links: Optional[Dict[str, Any]] = None

class UserResponse(UserBase):
    """Full user response including system fields"""
    id: UUID
    created_at: datetime
    music_profile: Optional['MusicProfileResponse'] = None

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

# Music Schemas
class Artist(BaseModel):
    """Spotify artist information"""
    id: str
    name: str
    genres: List[str]
    popularity: int
    image_url: Optional[str] = None

    class Config:
        orm_mode = True

class TopArtistsResponse(BaseModel):
    """Response model for top artists endpoint"""
    items: List[Artist]
    total: int
    time_range: str  # short_term, medium_term, or long_term

class TopGenresResponse(BaseModel):
    """Response model for top genres endpoint"""
    genres: List[str]
    time_range: str

class MutualMusicInterests(BaseModel):
    """Response model for mutual music interests"""
    mutual_artists: List[Artist]
    mutual_genres: List[str]
    compatibility_score: float  # percentage of musical compatibility

class TrackRecommendation(BaseModel):
    """Recommended track information"""
    id: str
    name: str
    artist: str
    album: str
    preview_url: Optional[str]
    image_url: Optional[str]

class MusicRecommendationsResponse(BaseModel):
    """Response model for music recommendations"""
    tracks: List[TrackRecommendation]
    seed_artists: List[str]
    seed_genres: List[str]

class Metrics(BaseModel):
    energy_score: float
    danceability_score: float
    diversity_score: float
    obscurity_score: float
    favorite_decades: List[str]
    listening_patterns: Dict[str, Any]
    listening_history: List[Dict[str, Any]]

    class Config:
        orm_mode = True
