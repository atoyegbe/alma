from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from datetime import datetime

from app.auth.auth import get_current_user
from app.database.database import db_dependency
from app.models.datamodels import User
from app.models.schema import PlaylistCreate, PlaylistUpdate, PlaylistResponse
from app.helpers.spotify import SpotifyClient, get_spotify_client

router = APIRouter()

@router.get("/", response_model=List[PlaylistResponse])
async def get_playlists(
    db: db_dependency,
    current_user: User = Depends(get_current_user)
):
    """Get current user's playlists"""
    spotify = await get_spotify_client(current_user.id, db)
    playlists = await spotify.get_user_playlists()
    return playlists

@router.get("/mutual/{user_id}", response_model=List[PlaylistResponse])
async def get_mutual_playlists(
    user_id: UUID,
    db: db_dependency,
    current_user: User = Depends(get_current_user)
):
    """Get mutual playlists between current user and specified user"""
    # Get both users' playlists
    current_spotify = await get_spotify_client(current_user.id, db)
    other_spotify = await get_spotify_client(str(user_id), db)
    
    # Get playlists for both users
    current_playlists = await current_spotify.get_user_playlists()
    other_playlists = await other_spotify.get_user_playlists()
    
    # Find mutual playlists (playlists that both users follow)
    current_playlist_ids = {p["id"] for p in current_playlists}
    other_playlist_ids = {p["id"] for p in other_playlists}
    mutual_ids = current_playlist_ids.intersection(other_playlist_ids)
    
    # Return mutual playlists with full details
    mutual_playlists = [p for p in current_playlists if p["id"] in mutual_ids]
    return mutual_playlists

@router.post("/", response_model=PlaylistResponse)
async def create_playlist(
    playlist_data: PlaylistCreate,
    db: db_dependency,
    current_user: User = Depends(get_current_user)
):
    """Create a new playlist"""
    spotify = await get_spotify_client(current_user.id, db)
    
    # Create playlist in Spotify
    playlist = await spotify.create_playlist(
        name=playlist_data.name,
        description=playlist_data.description,
        public=playlist_data.public
    )
    
    # Add tracks if provided
    if playlist_data.tracks:
        await spotify.add_tracks_to_playlist(
            playlist_id=playlist["id"],
            track_uris=playlist_data.tracks
        )
    
    return playlist

@router.put("/{playlist_id}", response_model=PlaylistResponse)
async def update_playlist(
    playlist_id: str,
    playlist_update: PlaylistUpdate,
    db: db_dependency,
    current_user: User = Depends(get_current_user)
):
    """Update an existing playlist"""
    spotify = await get_spotify_client(current_user.id, db)
    
    # Update playlist details
    updated_playlist = await spotify.update_playlist(
        playlist_id=playlist_id,
        name=playlist_update.name,
        description=playlist_update.description,
        public=playlist_update.public
    )
    
    # Update tracks if provided
    if playlist_update.tracks is not None:
        # Clear existing tracks
        await spotify.clear_playlist_tracks(playlist_id)
        # Add new tracks
        if playlist_update.tracks:
            await spotify.add_tracks_to_playlist(
                playlist_id=playlist_id,
                track_uris=playlist_update.tracks
            )
    
    return updated_playlist

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
