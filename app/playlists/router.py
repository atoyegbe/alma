from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from datetime import datetime

from app.auth.auth import get_current_user
from app.database.database import db_dependency
from app.models.datamodels import User
from app.models.schema import PlaylistCreate, PlaylistUpdate, PlaylistResponse
from app.helpers.spotify import get_spotify_client

from app.playlists.playlists import get_user_playlists, update_user_playlist, create_user_playlist, get_user_mutual_playlists

router = APIRouter()

@router.get("/", response_model=List[PlaylistResponse])
async def get_playlists(
    db: db_dependency,
    current_user: User = Depends(get_current_user)
):
    """Get current user's playlists"""
    return await get_user_playlists(db, current_user.id)

@router.get("/mutual/{user_id}", response_model=List[PlaylistResponse])
async def get_mutual_playlists(
    user_id: UUID,
    db: db_dependency,
    current_user: User = Depends(get_current_user)
):
    """Get mutual playlists between current user and specified user"""
    # Get both users' playlists
    return await get_user_mutual_playlists(target_user_id, user_id, db)

@router.post("/", response_model=PlaylistResponse)
async def create_playlist(
    playlist_data: PlaylistCreate,
    db: db_dependency,
    current_user: User = Depends(get_current_user)
):
    return await create_user_playlist(current_user.id, playlist_data, db) 

@router.put("/{playlist_id}", response_model=PlaylistResponse)
async def update_playlist(
    playlist_id: str,
    playlist_update: PlaylistUpdate,
    db: db_dependency,
    current_user: User = Depends(get_current_user)
):
    """Update an existing playlist"""
    return await update_playlist(playlist_id, playlist_update, db)

@router.delete("/{playlist_id}")
async def delete_playlist(
    playlist_id: str,
    db: db_dependency,
    current_user: User = Depends(get_current_user)
):
    """Delete a playlist"""
    spotify = await get_spotify_client(current_user.id, db)
    await spotify.delete_playlist(playlist_id)
    return {"message": "Playlist deleted successfully"}

@router.get("/{playlist_id}/tracks")
async def get_playlist_tracks(
    playlist_id: str,
    db: db_dependency,
    current_user: User = Depends(get_current_user)
):
    """Get tracks in a playlist"""
    spotify = await get_spotify_client(current_user.id, db)
    tracks = await spotify.get_playlist_tracks(playlist_id)
    return tracks
