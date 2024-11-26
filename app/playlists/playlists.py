
from typing import List
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.schema import PlaylistResponse, PlaylistCreate, PlaylistUpdate
from app.helpers.spotify import get_spotify_client



async def get_user_playlists(
    user_id: str,
    db: Session = Depends(get_db)
) -> List[PlaylistResponse]:
    spotify = await get_spotify_client(user_id, db)
    playlists = await spotify.get_user_playlists()
    return playlists


async def get_user_mutual_playlists(
    target_user_id: str,
    user_id: str,
    db: Session = Depends(get_db)
) -> List[PlaylistResponse]:
    """Get mutual playlists between current user and specified user"""
    # Get both users' playlists
    current_spotify = await get_spotify_client(target_user_id, db)
    other_spotify = await get_spotify_client(user_id, db)
    
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


async def create_user_playlist(
    user_id: str,
    playlist_data: PlaylistCreate,
    db: Session = Depends(get_db)
) -> PlaylistResponse:
    # TODO:  add error handling
    # TODO:  There should be a limit on tracks to be added to a playlist
    # TODO:  This should be  self generating playlist based on users taste
    spotify = await get_spotify_client(user_id, db)
    playlist = await spotify.create_playlist(**playlist_data)

    # Add tracks if provided
    if playlist_data.tracks:
        await spotify.add_tracks_to_playlist(
            playlist_id=playlist["id"],
            track_uris=playlist_data.tracks
        )
    
    return playlist

async def update_user_playlist(
    playlist_id: str,
    playlist_update: PlaylistUpdate,
    db: Session = Depends(get_db)
) -> PlaylistResponse:
    spotify = await get_spotify_client(user_id, db)
    Updated_playlist = await spotify.create_playlist(**playlist_data)
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