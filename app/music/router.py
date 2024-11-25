from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database.database import db_dependency
from app.auth.auth import get_current_user
from app.models.datamodels import User, MusicProfile
from app.models.schema import (
    TopArtistsResponse, TopGenresResponse,
    MutualMusicInterests, MusicRecommendationsResponse
)
from app.music import music

router = APIRouter()

@router.get("/top-artists", response_model=TopArtistsResponse)
async def get_top_artists(
    db: db_dependency,
    current_user: User = Depends(get_current_user),
    time_range: str = Query(
        "medium_term",
        description="Time range for top artists (short_term, medium_term, long_term)"
    ),
    limit: int = Query(20, ge=1, le=50)
):
    """Get current user's top artists from Spotify"""
    return await music.get_user_top_artists(
        db=db,
        user_id=current_user.id,
        time_range=time_range,
        limit=limit
    )

@router.get("/top-genres", response_model=TopGenresResponse)
async def get_top_genres(
    db: db_dependency,
    current_user: User = Depends(get_current_user),
    time_range: str = Query(
        "medium_term",
        description="Time range for top genres (short_term, medium_term, long_term)"
    )
):
    """Get current user's top genres based on their top artists"""
    return await music.get_user_top_genres(
        db=db,
        user_id=current_user.id,
        time_range=time_range
    )

@router.get("/recommendations", response_model=MusicRecommendationsResponse)
async def get_recommendations(
    db: db_dependency,
    current_user: User = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=50)
):
    """Get personalized music recommendations based on user's taste"""
    return await music.get_music_recommendations(
        db=db,
        user_id=current_user.id,
        limit=limit
    )

@router.get("/mutual/{user_id}", response_model=MutualMusicInterests)
async def get_mutual_interests(
    user_id: str,
    db: db_dependency,
    current_user: User = Depends(get_current_user)
):
    """Get mutual music interests with another user"""
    if str(current_user.id) == user_id:
        raise HTTPException(
            status_code=400,
            detail="Cannot get mutual interests with yourself"
        )
    
    return await music.get_mutual_music_interests(
        db=db,
        user1_id=current_user.id,
        user2_id=user_id
    )

@router.post("/spotify/sync")
async def sync_spotify_data(
    db: db_dependency,
    current_user: User = Depends(get_current_user)
):
    """Sync user's Spotify data"""
    await music.sync_user_spotify_data(current_user.id, db)
    return {"message": "Music profile updated successfully"}

@router.get("/profile/metrics")
async def get_profile_metrics(
    db: db_dependency,
    current_user: User = Depends(get_current_user)
):
    """Get user's music profile metrics"""
    profile = db.query(MusicProfile).filter(
        MusicProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Music profile not found")
    
    return {
        "favorite_decades": profile.favorite_decades,
        "energy_score": profile.energy_score,
        "danceability_score": profile.danceability_score,
        "diversity_score": profile.diversity_score,
        "obscurity_score": profile.obscurity_score
    }