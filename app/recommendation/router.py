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
    target_profile = current_profile.to_dict()

    other_profiles_dict = [
        profile.to_dict()
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
    profile1 = user1_profile.to_dict()
    profile2 = user2_profile.to_dict()
    
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
