from fastapi import APIRouter, Depends
from typing import List
from uuid import UUID

from app.auth.auth import get_authenticated_user
from app.users.users import UserService
from app.helpers.router.utils import get_user_service
from app.models.models import User, MusicProfile
from app.models.schema import UserUpdate, SocialLinks

router = APIRouter()


@router.get("/me", response_model=User)
async def get_current_user_profile(
    current_user: User = Depends(get_authenticated_user)
):
    """Get current user's profile"""
    return current_user


@router.get("/me/music-profile", response_model=MusicProfile)
async def get_current_user_music_profile(
    current_user: User = Depends(get_authenticated_user),
    user_service: UserService = Depends(get_user_service),
):
    """Get current user's music profile"""
    return user_service.get_music_profile(current_user.id)


@router.put("/me", response_model=User)
async def update_current_user_profile(
    profile_update: UserUpdate,
    current_user: User = Depends(get_authenticated_user),
    user_service: UserService = Depends(get_user_service),
):
    """Update current user's profile"""
    return user_service.update_user(
        current_user.id, profile_update.model_dump(exclude_unset=True)
    )


@router.put("/me/social-links", response_model=User)
async def update_user_social_links(
    social_links: SocialLinks,
    current_user: User = Depends(get_authenticated_user),
    user_service: UserService = Depends(get_user_service),
):
    """Update user's social media links"""
    return user_service.update_social_links(current_user.id, social_links)


@router.get("/{user_id}", response_model=User)
async def get_user_profile(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
):
    """Get public profile of a user"""
    return user_service.get_user(user_id)


@router.get("/{user_id}/music-profile", response_model=MusicProfile)
async def get_user_music_profile(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
):
    """Get music profile of a user"""
    return user_service.get_music_profile(user_id)


@router.get("/recommendations", response_model=List[User])
async def get_user_recommendations(
    limit: int = 10,
    current_user: User = Depends(get_authenticated_user),
    user_service: UserService = Depends(get_user_service),
):
    """Get recommended users based on music taste"""
    return user_service.get_recommended_users(current_user.id, limit)
