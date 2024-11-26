from typing import Dict, Any, Optional, List
from sqlmodel import SQLModel

class SimilarityPercentage(SQLModel):
    similarity_score: int

class SharedMusic(SQLModel):
    artists: List[Dict[str, Any]]
    tracks: List[Dict[str, Any]]
    genres: List[str]

class UserCompatibility(SQLModel):
    overall_similarity: float
    genre_similarity: float
    artist_similarity: float
    diversity_similarity: float
    obscurity_similarity: float
    decade_similarity: float
    listening_pattern_similarity: float
    shared_music: SharedMusic

class RecommendedUser(SQLModel):
    user_id: str
    username: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    similarity_score: float
    compatibility: UserCompatibility