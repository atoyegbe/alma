from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException

from app.models.datamodels import (
    User, MusicProfile 
)
from app.models.schema import UserUpdate, SocialLinks, MusicProfileResponse, UserResponse
from app.database.database import get_db
from app.recommendation.music_recommender import MusicRecommender

_recommender = MusicRecommender()


def get_user(db: Session, user_id: int) -> User:
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).options(
        joinedload(User.music_profile)
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_user_by_spotify_id(db: Session, spotify_id: str) -> Optional[User]:
    """Get user by Spotify ID"""
    return db.query(User).filter(User.spotify_id == spotify_id).options(
        joinedload(User.music_profile)
    ).first()

def get_user_by_token(db: Session, auth_token: str) -> Optional[User]:
    """Get user by authentication token"""
    user = db.query(User).filter(User.spotify_token == auth_token).options(
        joinedload(User.music_profile)
    ).first()
    return user

def get_music_profile(db: Session, user_id: int) -> MusicProfile:
    """Get user's music profile alone"""
    profile = db.query(MusicProfile).filter(MusicProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Music profile not found")
    return profile

def update_user_profile(db: Session, user_id: int, profile_data: dict) -> User:
    """Update user profile"""
    user = get_user_by_id(db, user_id)
    
    for key, value in profile_data.items():
        if hasattr(user, key):
            setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user

def create_user(db: Session, user_data: dict) -> User:
    """Create a new user with Spotify data"""
    # Check if user already exists
    existing_user = get_user_by_spotify_id(db, user_data["spotify_id"])
    if existing_user:
        return existing_user
    
    # Create new user
    user = User(
        spotify_id=user_data["spotify_id"],
        spotify_token=user_data["access_token"],
        spotify_refresh_token=user_data["refresh_token"],
        name=user_data["name"],
        email=user_data["email"],
        profile_image=user_data.get("profile_image"),
        is_active=True
    )
    
    # Create empty music profile
    music_profile = MusicProfile(
        genres=[],
        top_artists=[],
        top_tracks=[],
        favorite_decades=[],
        energy_score=0.0,
        danceability_score=0.0,
        diversity_score=0.0,
        obscurity_score=0.0,
        listening_history=[]
    )
    
    user.music_profile = music_profile
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_social_links(db: Session, user_id: int, social_links: SocialLinks) -> User:
    """Update user's social media links"""
    user = get_user_by_id(db, user_id)
    
    # Convert social links to dictionary and update user's social_links JSON column
    user.social_links = social_links.dict(exclude_unset=True)
    
    db.commit()
    db.refresh(user)
    return user

def get_recommended_users(db: Session, user_id: int, limit: int = 10) -> List[User]:
    """Get recommended users based on music taste using the advanced recommendation engine"""
    current_user = get_user_by_id(db, user_id)
    if not current_user or not current_user.music_profile:
        return []
    
    # Get all users with their music profiles except current user
    all_users = db.query(User).filter(User.id != user_id).options(
        joinedload(User.music_profile)
    ).all()
    
    if not all_users:
        return []
    
    # Convert current user's profile to dictionary format
    target_profile = {
        "id": current_user.id,
        "genres": current_user.music_profile.genres,
        "top_artists": current_user.music_profile.top_artists,
        "top_tracks": current_user.music_profile.top_tracks,
        "favorite_decades": current_user.music_profile.favorite_decades,
        "energy_score": current_user.music_profile.energy_score,
        "danceability_score": current_user.music_profile.danceability_score,
        "diversity_score": current_user.music_profile.diversity_score,
        "obscurity_score": current_user.music_profile.obscurity_score,
        "listening_history": current_user.music_profile.listening_history
    }
    
    # Convert other users' profiles to dictionary format
    other_profiles = [
        {
            "id": user.id,
            "genres": user.music_profile.genres if user.music_profile else [],
            "top_artists": user.music_profile.top_artists if user.music_profile else [],
            "top_tracks": user.music_profile.top_tracks if user.music_profile else [],
            "favorite_decades": user.music_profile.favorite_decades if user.music_profile else [],
            "energy_score": user.music_profile.energy_score if user.music_profile else 0.0,
            "danceability_score": user.music_profile.danceability_score if user.music_profile else 0.0,
            "diversity_score": user.music_profile.diversity_score if user.music_profile else 0.0,
            "obscurity_score": user.music_profile.obscurity_score if user.music_profile else 0.0,
            "listening_history": user.music_profile.listening_history if user.music_profile else []
        }
        for user in all_users if user.music_profile
    ]
    
    # Get recommendations using the advanced recommendation engine
    recommendations = _recommender.get_user_recommendations(target_profile, other_profiles)
    
    # Sort users based on recommendation scores and return top matches
    recommended_user_ids = [rec["user_id"] for rec in recommendations[:limit]]
    recommended_users = [user for user in all_users if user.id in recommended_user_ids]
    
    # Sort recommended_users to maintain the order from recommendations
    return sorted(recommended_users, key=lambda u: recommended_user_ids.index(u.id))
