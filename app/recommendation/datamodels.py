from typing import List, Dict, Any, Optional
from sqlmodel import SQLModel


class SimilarityPercentage(SQLModel):
    similarity_score: Optional[int] = None


class SharedMusic(SQLModel):
    artists: Optional[List[Dict[str, Any]]] = None
    tracks: Optional[List[Dict[str, Any]]] = None
    genres: Optional[List[str]] = None


class UserCompatibility(SQLModel):
    overall_similarity: Optional[float] = None
    genre_similarity: Optional[float] = None
    artist_similarity: Optional[float] = None
    diversity_similarity: Optional[float] = None
    obscurity_similarity: Optional[float] = None
    decade_similarity: Optional[float] = None
    track_similarity: Optional[float] = None
    listening_pattern_similarity: Optional[float] = None
    shared_music: Optional[SharedMusic] = None


class RecommendedUser(SQLModel):
    user_id: Optional[str] = None
    similarity_score: Optional[float] = None
    compatibility: Optional[UserCompatibility] = None
    username: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
