from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID
from sqlmodel import Session, select

from app.database.database import db_dependency
from app.auth.auth import get_current_user
from app.models.sqlmodels import User, MusicProfile
from app.recommendation.music_recommender import MusicRecommender
from app.recommendation.datamodels import RecommendedUser, UserCompatibility, SharedMusic

router = APIRouter()
recommender = MusicRecommender()

@router.get("/recommendations/users", response_model=List[RecommendedUser])
async def get_recommended_users(
    db: db_dependency, 
    current_user: User = Depends(get_current_user),
):
    """Get recommended users based on music taste"""
    # Get current user's music profile
    statement = select(MusicProfile).where(MusicProfile.user_id == current_user.id)
    current_profile = db.exec(statement).first()
    
    if not current_profile:
        raise HTTPException(status_code=404, detail="Music profile not found")
    
    # Get all other users' profiles
    statement = select(MusicProfile, User).where(
        MusicProfile.user_id != current_user.id,
        User.id == MusicProfile.user_id
    )
    results = db.exec(statement).all()
    
    if not results:
        return []
    
    # Convert profiles to dictionaries
    target_profile = current_profile.to_dict()
    other_profiles = []
    other_profiles_map = {}
    user_map = {}
    
    for profile, user in results:
        other_profiles.append(profile.to_dict())
        other_profiles_map[str(user.id)] = profile
        user_map[str(user.id)] = user
    
    # Get recommendations
    recommendations = recommender.get_user_recommendations(
        target_profile,
        other_profiles
    )
    
    # Enhance recommendations with user details
    enhanced_recommendations = []
    for rec in recommendations:
        user = user_map.get(rec["user_id"])
        if user:
            # Get shared music details for this user
            shared_artists = set(a["id"] for a in current_profile.top_artists) & set(a["id"] for a in other_profiles_map[rec["user_id"]].top_artists)
            shared_tracks = set(t["id"] for t in current_profile.top_tracks) & set(t["id"] for t in other_profiles_map[rec["user_id"]].top_tracks)
            shared_genres = set(current_profile.genres) & set(other_profiles_map[rec["user_id"]].genres)
            
            shared_music = SharedMusic(
                artists=[a for a in current_profile.top_artists if a["id"] in shared_artists],
                tracks=[t for t in current_profile.top_tracks if t["id"] in shared_tracks],
                genres=list(shared_genres)
            )
            
            compatibility = UserCompatibility(
                overall_similarity=rec["similarity"],
                genre_similarity=rec["details"]["genre_similarity"],
                artist_similarity=rec["details"]["artist_similarity"],
                diversity_similarity=rec["details"]["diversity_similarity"],
                obscurity_similarity=rec["details"]["obscurity_similarity"],
                decade_similarity=rec["details"]["decade_similarity"],
                listening_pattern_similarity=rec["details"]["listening_pattern_similarity"],
                shared_music=shared_music
            )
            
            recommended_user = RecommendedUser(
                user_id=str(user.id),
                username=user.username,
                display_name=user.display_name,
                avatar_url=user.avatar_url,
                similarity_score=rec["similarity"],
                compatibility=compatibility
            )
            enhanced_recommendations.append(recommended_user)
    
    return enhanced_recommendations

@router.get("/recommendations/compatibility/{user_id}", response_model=UserCompatibility)
async def get_user_compatibility(
    user_id: UUID,
    db: db_dependency,
    current_user: User = Depends(get_current_user)
):
    """Get detailed compatibility analysis with another user"""
    # Get target user's profile
    statement = select(MusicProfile).where(MusicProfile.user_id == user_id)
    target_profile = db.exec(statement).first()
    if not target_profile:
        raise HTTPException(status_code=404, detail="Target user's music profile not found")
    
    # Get current user's profile
    statement = select(MusicProfile).where(MusicProfile.user_id == current_user.id)
    current_profile = db.exec(statement).first()
    if not current_profile:
        raise HTTPException(status_code=404, detail="Current user's music profile not found")
    
    # Calculate compatibility
    similarity = recommender.calculate_overall_similarity(
        current_profile.to_dict(),
        target_profile.to_dict()
    )
    
    # Add shared music details
    shared_artists = set(a["id"] for a in current_profile.top_artists) & set(a["id"] for a in target_profile.top_artists)
    shared_tracks = set(t["id"] for t in current_profile.top_tracks) & set(t["id"] for t in target_profile.top_tracks)
    shared_genres = set(current_profile.genres) & set(target_profile.genres)
    
    shared_music = SharedMusic(
        artists=[a for a in current_profile.top_artists if a["id"] in shared_artists],
        tracks=[t for t in current_profile.top_tracks if t["id"] in shared_tracks],
        genres=list(shared_genres)
    )
    
    return UserCompatibility(
        overall_similarity=similarity["overall"],
        genre_similarity=similarity["genre_similarity"],
        artist_similarity=similarity["artist_similarity"],
        diversity_similarity=similarity["diversity_similarity"],
        obscurity_similarity=similarity["obscurity_similarity"],
        decade_similarity=similarity["decade_similarity"],
        listening_pattern_similarity=similarity["listening_pattern_similarity"],
        shared_music=shared_music
    )
