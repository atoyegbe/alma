from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlmodel import SQLModel, Field


# Social Links Schema
class SocialLinks(SQLModel):
    """Model for social media links"""

    instagram: Optional[str] = Field(None, description="Instagram username")
    twitter: Optional[str] = Field(None, description="Twitter username")
    facebook: Optional[str] = Field(None, description="Facebook profile URL")
    spotify: Optional[str] = Field(None, description="Spotify profile URL")


# Request/Response Models that differ from DB Models
class MusicProfileUpdate(SQLModel):
    """Attributes that can be updated in a music profile"""

    top_artists: Optional[List[Dict[str, Any]]] = None
    top_genres: Optional[List[str]] = None
    music_soul_level: Optional[int] = None


class UserUpdate(SQLModel):
    """Attributes that can be updated"""

    name: Optional[str] = None
    image_url: Optional[str] = None
    social_links: Optional[Dict[str, Any]] = None


# Music API Response Models
class Artist(SQLModel):
    """Spotify artist information"""

    id: str
    name: str
    genres: List[str]
    popularity: int
    image_url: Optional[str] = None


class TopArtistsResponse(SQLModel):
    """Response model for top artists endpoint"""

    items: List[Artist]
    total: int
    time_range: str  # short_term, medium_term, or long_term


class TopGenresResponse(SQLModel):
    """Response model for top genres endpoint"""

    genres: List[str]
    time_range: str


class MutualMusicInterests(SQLModel):
    """Response model for mutual music interests"""

    mutual_artists: List[Artist]
    mutual_genres: List[str]
    compatibility_score: float  # percentage of musical compatibility


class TrackRecommendation(SQLModel):
    """Recommended track information"""

    id: str
    name: str
    artist: str
    album: str
    preview_url: Optional[str]
    image_url: Optional[str]


class MusicRecommendationsResponse(SQLModel):
    """Response model for music recommendations"""

    tracks: List[TrackRecommendation]
    seed_artists: List[str]
    seed_genres: List[str]


class Metrics(SQLModel):
    """Music metrics information"""

    energy_score: float
    danceability_score: float
    diversity_score: float
    obscurity_score: float
    favorite_decades: List[str]
    listening_patterns: Dict[str, Any]
    listening_history: List[Dict[str, Any]]


# Playlist models for request/response validation
class PlaylistBase(SQLModel):
    name: str
    description: Optional[str] = None
    public: Optional[bool] = True
    tracks: Optional[List[str]] = None


class PlaylistCreate(PlaylistBase):
    pass


class PlaylistUpdate(PlaylistBase):
    name: Optional[str] = None
    public: Optional[bool] = None


class PlaylistResponse(PlaylistBase):
    id: str
    owner: Dict[str, str]
    spotify_id: str
    created_at: str
    updated_at: str
    tracks: Dict[str, List[str]]

    class Config:
        orm_mode = True
