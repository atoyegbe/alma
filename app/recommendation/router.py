from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List, Optional
from uuid import UUID
from sqlmodel import or_, select

from app.helpers.router.utils import get_user_service
from app.users.users import UserService
from app.auth.auth import get_authenticated_user
from app.models.models import User, MusicProfile
from app.recommendation.music_recommender import MusicRecommender
from app.recommendation.datamodels import (
    RecommendedUser,
    UserCompatibility,
    SharedMusic,
)

router = APIRouter()
recommender = MusicRecommender()


@router.get("/users", response_model=List[RecommendedUser])
async def get_recommended_users(
    request: Request,
    limit: int = 10,
    min_score: float = 0.0,
    genres: Optional[List[str]] = None,
    current_user: User = Depends(get_authenticated_user),
):
    """Get recommended users based on music taste"""
    # Get current user's music profile
    current_profile = request.app.get(MusicProfile, current_user.id)
    if not current_profile:
        raise HTTPException(status_code=404, detail="Music profile not found")

    # Get all other users' profiles
    # If genres contains values: The query filters based on the or_ conditions.
    # If genres is empty: The 1 == 1 condition keeps the query valid without applying any additional filtering.
    statement = select(MusicProfile, User).where(
        MusicProfile.user_id != current_user.id,
        User.id == MusicProfile.user_id,
        (
            or_(MusicProfile.genres.contains(genre) for genre in genres)
            if genres
            else (1 == 1)
        ),
    )
    results = request.state.db.exec(statement).all()

    if not results:
        return []

    # Convert profiles to dictionaries
    other_profiles = []
    other_profiles_map = {}
    user_map = {}

    for profile, user in results:
        other_profiles.append(profile)
        other_profiles_map[str(user.id)] = profile
        user_map[str(user.id)] = user

    # Get recommendations
    recommendations: List[RecommendedUser] = recommender.get_user_recommendations(
        current_profile, other_profiles, limit=limit
    )

    # Enhance recommendations with user details
    enhanced_recommendations = []
    for rec in recommendations:
        user = user_map.get(rec["user_id"])
        if user:
            # Get shared music details for this user
            shared_music = _get_shared_music(
                current_profile, other_profiles_map[rec["user_id"]]
            )
            rec.compatibility.shared_music = shared_music

            rec.username = user.username
            rec.display_name = user.display_name
            rec.avatar_url = user.avatar_url

            enhanced_recommendations.append(rec)

    return enhanced_recommendations


@router.get("/compatibility/{user_id}", response_model=UserCompatibility)
async def get_user_compatibility(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_authenticated_user)
):
    """Get detailed compatibility analysis with another user"""
    return user_service.get_user_compatibility(
        current_user.id, user_id
    )


def _get_shared_music(profile1: MusicProfile, profile2: MusicProfile) -> SharedMusic:
    """Calculate shared music between two profiles."""
    shared_music = SharedMusic(
        artists=list(set(profile1.top_artists) & set(profile2.top_artists)),
        tracks=list(set(profile1.top_tracks) & set(profile2.top_tracks)),
        genres=list(set(profile1.genres) & set(profile2.genres)),
    )
    return shared_music
