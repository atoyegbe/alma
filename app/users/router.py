from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.database import db_dependency
from app.auth.auth import get_current_user
from app.models.datamodels import User, MusicProfile
from app.models.schema import UserUpdate, MusicProfileResponse, UserResponse
from app.users import users

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    db: db_dependency,
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile"""
    return current_user

@router.get("/me/music-profile", response_model=MusicProfileResponse)
async def get_current_user_music_profile(
    db: db_dependency,
    current_user: User = Depends(get_current_user)
):
    """Get current user's music profile"""
    return users.get_music_profile(db, current_user.id)

@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    profile_update: UserUpdate,
    db: db_dependency,
    current_user: User = Depends(get_current_user)
):
    """Update current user's profile"""
    return users.update_user_profile(db, current_user.id, profile_update.dict(exclude_unset=True))

@router.put("/me/social-links", response_model=UserResponse)
async def update_user_social_links(
    social_links: SocialLinks,
    db: db_dependency,
    current_user: User = Depends(get_current_user)
):
    """Update user's social media links"""
    return users.update_social_links(db, current_user.id, social_links)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_profile(
    user_id: int,
    db: db_dependency,
    current_user: User = Depends(get_current_user)
):
    """Get public profile of a user"""
    return users.get_user(db, user_id)

@router.get("/{user_id}/music-profile", response_model=MusicProfileResponse)
async def get_user_music_profile(
    user_id: int,
    db: db_dependency,
    current_user: User = Depends(get_current_user)
):
    """Get music profile of a user"""
    return users.get_music_profile(db, user_id)

@router.get("/recommendations", response_model=List[UserResponse])
async def get_user_recommendations(
    db: db_dependency,
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """Get recommended users based on music taste"""
    return users.get_recommended_users(db, current_user.id, limit)
