from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from datetime import datetime
import httpx

from app.auth.auth import requires_auth, get_header
from app.database.database import get_db
from app.models.schema import PlaylistCreate, PlaylistUpdate, PlaylistResponse, UserResponse
from app.helpers.spotify import create_spotify_playlist, update_spotify_playlist, delete_spotify_playlist, add_tracks_to_playlist, clear_playlist_tracks, get_playlist_tracks
from app.constant import API_BASE_URL

router = APIRouter()

@router.get("/playlists", dependencies=[Depends(requires_auth)])
async def get_playlists(token: str):
    try:
        response = await httpx.AsyncClient().get(
            f"{API_BASE_URL}me/playlists", headers=get_header(token)
        )
        playlists = response.json()
        return playlists
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")

@router.get("/mutual/{user_id}", response_model=List[PlaylistResponse])
async def get_mutual_playlists(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(requires_auth)
):
    """Get mutual playlists between current user and specified user"""
    # Get both users' playlists from Spotify
    headers = get_header(current_user.auth_token)
    
    # Get current user's playlists
    async with httpx.AsyncClient() as client:
        current_user_response = await client.get(
            f"{API_BASE_URL}me/playlists",
            headers=headers
        )
        current_user_playlists = current_user_response.json()["items"]
        
        # Get other user's public playlists
        other_user_response = await client.get(
            f"{API_BASE_URL}users/{user_id}/playlists",
            headers=headers
        )
        other_user_playlists = other_user_response.json()["items"]
    
    # Find mutual playlists (this is a simplified version - you might want to add more sophisticated matching)
    mutual_playlists = []
    current_user_tracks = {playlist["id"]: set(get_playlist_tracks(playlist["id"])) for playlist in current_user_playlists}
    other_user_tracks = {playlist["id"]: set(get_playlist_tracks(playlist["id"])) for playlist in other_user_playlists}
    
    for current_playlist_id, current_tracks in current_user_tracks.items():
        for other_playlist_id, other_tracks in other_user_tracks.items():
            similarity = len(current_tracks.intersection(other_tracks)) / len(current_tracks.union(other_tracks))
            if similarity > 0.5:  # You can adjust this threshold
                mutual_playlists.append(current_playlist_id)
                break
    
    return mutual_playlists

@router.post("/create", response_model=PlaylistResponse)
async def create_playlist(
    playlist: PlaylistCreate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(requires_auth)
):
    """Create a new playlist"""
    try:
        # Create playlist in Spotify
        spotify_playlist = await create_spotify_playlist(
            user_id=current_user.spotify_id,
            token=current_user.auth_token,
            name=playlist.name,
            description=playlist.description,
            public=playlist.public
        )
        
        # Add tracks if provided
        if playlist.tracks:
            track_uris = [track["uri"] for track in playlist.tracks]
            await add_tracks_to_playlist(
                playlist_id=spotify_playlist["id"],
                track_uris=track_uris,
                token=current_user.auth_token
            )
        
        return PlaylistResponse(
            id=spotify_playlist["id"],
            owner_id=current_user.id,
            name=playlist.name,
            description=playlist.description,
            public=playlist.public,
            tracks=playlist.tracks,
            created_at=datetime.utcnow()
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{playlist_id}", response_model=PlaylistResponse)
async def update_playlist(
    playlist_id: str,
    playlist_update: PlaylistUpdate,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(requires_auth)
):
    """Update an existing playlist"""
    try:
        # Update playlist in Spotify
        updated_playlist = await update_spotify_playlist(
            playlist_id=playlist_id,
            token=current_user.auth_token,
            name=playlist_update.name,
            description=playlist_update.description,
            public=playlist_update.public
        )
        
        # Update tracks if provided
        if playlist_update.tracks:
            # Clear existing tracks
            await clear_playlist_tracks(playlist_id, current_user.auth_token)
            # Add new tracks
            track_uris = [track["uri"] for track in playlist_update.tracks]
            await add_tracks_to_playlist(
                playlist_id=playlist_id,
                track_uris=track_uris,
                token=current_user.auth_token
            )
        
        return PlaylistResponse(
            id=updated_playlist["id"],
            owner_id=current_user.id,
            name=playlist_update.name,
            description=playlist_update.description,
            public=playlist_update.public,
            tracks=playlist_update.tracks,
            created_at=datetime.utcnow()
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{playlist_id}")
async def delete_playlist(
    playlist_id: str,
    db: Session = Depends(get_db),
    current_user: UserResponse = Depends(requires_auth)
):
    """Delete a playlist"""
    try:
        # Delete playlist in Spotify
        await delete_spotify_playlist(
            playlist_id=playlist_id,
            token=current_user.auth_token
        )
        
        return {"message": "Playlist deleted successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
