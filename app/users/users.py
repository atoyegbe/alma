from typing import List, Optional, Dict
from uuid import UUID
from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.models import User, MusicProfile
from app.models.schema import SocialLinks
from app.recommendation.music_recommender import MusicRecommender

_recommender = MusicRecommender()


def get_user(db: Session, user_id: UUID) -> User:
    """Get user by ID"""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_user_by_spotify_id(db: Session, spotify_id: str) -> Optional[User]:
    """Get user by Spotify ID"""
    statement = select(User).where(User.spotify_id == spotify_id)
    return db.exec(statement).first()


def get_user_by_token(db: Session, auth_token: str) -> Optional[User]:
    """Get user by authentication token"""
    statement = select(User).where(User.spotify_token == auth_token)
    return db.exec(statement).first()


def get_music_profile(db: Session, user_id: UUID) -> MusicProfile:
    """Get user's music profile alone"""
    statement = select(MusicProfile).where(MusicProfile.user_id == user_id)
    profile = db.exec(statement).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Music profile not found")
    return profile


def update_user_profile(db: Session, user_id: UUID, profile_data: Dict) -> User:
    """Update user profile"""
    user = get_user(db, user_id)

    for key, value in profile_data.items():
        if hasattr(user, key):
            setattr(user, key, value)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_user(db: Session, user_data: Dict) -> User:
    """Create a new user with Spotify data"""
    # Check if user already exists
    existing_user = get_user_by_spotify_id(db, user_data["spotify_id"])
    if existing_user:
        return existing_user

    # Create new user
    user = User(
        spotify_id=user_data["spotify_id"],
        email=user_data["email"],
        display_name=user_data.get("display_name"),
        spotify_url=user_data.get("spotify_url"),
        spotify_image_url=user_data.get("images", [{}])[0].get("url"),
        country=user_data.get("country"),
        spotify_token=user_data.get("access_token"),
        spotify_refresh_token=user_data.get("refresh_token"),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Create empty music profile
    profile = MusicProfile(user_id=user.id)
    db.add(profile)
    db.commit()

    return user


def update_social_links(db: Session, user_id: UUID, social_links: SocialLinks) -> User:
    """Update user's social media links"""
    user = get_user(db, user_id)
    user.social_links = social_links.model_dump()
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_recommended_users(db: Session, user_id: UUID, limit: int = 10) -> List[User]:
    """Get recommended users based on music taste"""
    # Get current user's profile
    user_profile = get_music_profile(db, user_id)
    if not user_profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    # Get all other users
    statement = select(User).where(User.id != user_id)
    other_users = db.exec(statement).all()

    # Get recommendations using the music recommender
    recommended_users = _recommender.get_user_recommendations(
        user_profile, other_users, limit=limit
    )

    return recommended_users
