from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict

from app.database.database import db_dependency
from app.auth.auth import get_current_user
from app.models.datamodels import User, MusicProfile
from app.recommendation.music_recommender import MusicRecommender

router = APIRouter()
recommender = MusicRecommender()

@router.get("/recommendations/users")
async def get_recommended_users(
    db: db_dependency, 
    current_user: User = Depends(get_current_user),
) -> List[dict]:
    """Get recommended users based on music taste"""
    # Get current user's music profile
    current_profile = db.query(MusicProfile).filter(
        MusicProfile.user_id == current_user.id
    ).first()
    
    if not current_profile:
        raise HTTPException(status_code=404, detail="Music profile not found")
    
    # Get all other users' profiles
    other_profiles = db.query(MusicProfile).filter(
        MusicProfile.user_id != current_user.id
    ).all()
    
    if not other_profiles:
        return []
    
    # Convert profiles to dictionaries
    target_profile = {
        "id": current_user.id,
            "genres": current_profile.genres,
            "top_artists": current_profile.top_artists,
            "top_tracks": current_profile.top_tracks,
            "favorite_decades": current_profile.favorite_decades,
            "energy_score": current_profile.energy_score,
            "danceability_score": current_profile.danceability_score,
            "diversity_score": current_profile.diversity_score,
            "obscurity_score": current_profile.obscurity_score,
            "listening_history": current_profile.listening_history
    }
    
    other_profiles_dict = [
        {
            "id": profile.user_id,
            "genres": profile.genres,
            "top_artists": profile.top_artists,
            "top_tracks": profile.top_tracks,
            "favorite_decades": profile.favorite_decades,
            "energy_score": profile.energy_score,
            "danceability_score": profile.danceability_score,
            "diversity_score": profile.diversity_score,
            "obscurity_score": profile.obscurity_score,
            "listening_history": profile.listening_history
        }
        for profile in other_profiles
    ]
    
    # Get recommendations
    recommendations = recommender.get_user_recommendations(
        target_profile,
        other_profiles_dict
    )
    
    # Enhance recommendations with user details
    enhanced_recommendations = []
    for rec in recommendations:
        user = db.query(User).filter(User.id == rec["user_id"]).first()
        if user:
            enhanced_recommendations.append({
                **rec,
                "display_name": user.display_name,
                "spotify_url": user.spotify_url,
                "spotify_image_url": user.spotify_image_url,
                "country": user.country
            })
    
    return enhanced_recommendations

@router.get("/recommendations/compatibility/{user_id}")
async def get_user_compatibility(
    user_id: str,
    db: db_dependency,
    current_user: User = Depends(get_current_user)
) -> Dict:
    """Get detailed compatibility analysis with another user"""
    # Get both users' profiles
    user1_profile = db.query(MusicProfile).filter(
        MusicProfile.user_id == current_user.id
    ).first()
    user2_profile = db.query(MusicProfile).filter(
        MusicProfile.user_id == user_id
    ).first()
    
    if not user1_profile or not user2_profile:
        raise HTTPException(status_code=404, detail="Music profile not found")
    
    # Convert profiles to dictionaries
    profile1 = {
        "id": current_user.id,
        "genres": user1_profile.genres,
        "top_artists": user1_profile.top_artists,
        "top_tracks": user1_profile.top_tracks,
        "favorite_decades": user1_profile.favorite_decades,
        "energy_score": user1_profile.energy_score,
        "danceability_score": user1_profile.danceability_score,
        "diversity_score": user1_profile.diversity_score,
        "obscurity_score": user1_profile.obscurity_score,
        "listening_history": user1_profile.listening_history
    }
    
    profile2 = {
        "id": user_id,
        "genres": user2_profile.genres,
        "top_artists": user2_profile.top_artists,
        "top_tracks": user2_profile.top_tracks,
        "favorite_decades": user2_profile.favorite_decades,
        "energy_score": user2_profile.energy_score,
        "danceability_score": user2_profile.danceability_score,
        "diversity_score": user2_profile.diversity_score,
        "obscurity_score": user2_profile.obscurity_score,
        "listening_history": user2_profile.listening_history
    }
    
    # Get detailed compatibility analysis
    compatibility = recommender.calculate_overall_similarity(profile1, profile2)
    
    # Add shared music details
    shared_artists = set(a["id"] for a in user1_profile.top_artists) & set(a["id"] for a in user2_profile.top_artists)
    shared_tracks = set(t["id"] for t in user1_profile.top_tracks) & set(t["id"] for t in user2_profile.top_tracks)
    shared_genres = set(user1_profile.genres) & set(user2_profile.genres)
    
    return {
        "overall_compatibility": compatibility["overall_similarity"],
        "compatibility_breakdown": compatibility["component_similarities"],
        "shared_music": {
            "artists": [a for a in user1_profile.top_artists if a["id"] in shared_artists],
            "tracks": [t for t in user1_profile.top_tracks if t["id"] in shared_tracks],
            "genres": list(shared_genres)
        }
    }
