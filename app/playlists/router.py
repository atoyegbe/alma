from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from typing import List
from sqlmodel import select, Session

from app.auth.auth import get_authenticated_user
from app.database.database import get_db
from app.models.models import User, Playlist
from app.models.schema import PlaylistCreate, PlaylistUpdate, PlaylistResponse
from app.helpers.spotify import get_spotify_client
from app.playlists.playlists import (
    get_user_playlists,
    update_user_playlist,
    create_user_playlist,
    get_user_mutual_playlists,
)

router = APIRouter()


@router.get("/", response_model=List[PlaylistResponse])
async def list_playlists(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user)
):
    """Get current user's playlists"""
    return await get_user_playlists(db, current_user.id)


@router.get("/mutual/{user_id}", response_model=List[PlaylistResponse])
async def get_mutual_playlists(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user)
):
    """Get mutual playlists between current user and specified user"""
    if current_user.id == user_id:
        raise HTTPException(
            status_code=400, detail="Cannot get mutual playlists with yourself"
        )
    return await get_user_mutual_playlists(current_user.id, user_id, db)


@router.post("/", response_model=PlaylistResponse)
async def create_playlist(
    playlist_data: PlaylistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    """Create a new playlist"""
    return await create_user_playlist(current_user.id, playlist_data, db)


@router.put("/{playlist_id}", response_model=PlaylistResponse)
async def update_playlist(
    playlist_id: UUID,
    playlist_update: PlaylistUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    """Update an existing playlist"""
    # Verify playlist exists and belongs to user
    statement = select(Playlist).where(
        (Playlist.id == playlist_id) & (Playlist.user_id == current_user.id)
    )
    playlist = db.exec(statement).first()
    if not playlist:
        raise HTTPException(
            status_code=404,
            detail="Playlist not found or you don't have permission to update it",
        )

    return await update_user_playlist(playlist_id, playlist_update, db)


@router.delete("/{playlist_id}")
async def delete_playlist(
    playlist_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user)
):
    """Delete a playlist"""
    # Verify playlist exists and belongs to user
    statement = select(Playlist).where(
        (Playlist.id == playlist_id) & (Playlist.user_id == current_user.id)
    )
    playlist = db.exec(statement).first()
    if not playlist:
        raise HTTPException(
            status_code=404,
            detail="Playlist not found or you don't have permission to delete it",
        )

    # Delete from Spotify
    spotify = await get_spotify_client(current_user.id, db)
    await spotify.delete_playlist(str(playlist_id))

    # Delete from our database
    db.delete(playlist)
    db.commit()

    return {"message": "Playlist deleted successfully"}


# @router.get("/{playlist_id}/tracks", response_model=List[TrackResponse])
# async def get_playlist_tracks(
#     playlist_id: UUID,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_authenticated_user)
# ):
#     """Get tracks in a playlist"""
#     # Verify playlist exists
#     statement = select(Playlist).where(Playlist.id == playlist_id)
#     playlist = db.exec(statement).first()
#     if not playlist:
#         raise HTTPException(status_code=404, detail="Playlist not found")

#     spotify = await get_spotify_client(current_user.id, db)
#     tracks = await spotify.get_playlist_tracks(str(playlist_id))
#     return tracks
