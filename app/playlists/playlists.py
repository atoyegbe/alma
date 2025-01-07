from typing import List
from uuid import UUID
from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.schema import PlaylistResponse, PlaylistCreate, PlaylistUpdate
from app.models.models import Playlist, User
from app.helpers.spotify import get_spotify_client


async def get_user_playlists(db: Session, user_id: UUID) -> List[PlaylistResponse]:
    """Get user's playlists from both Spotify and our database"""
    # Get playlists from Spotify
    spotify = await get_spotify_client(user_id, db)
    spotify_playlists = await spotify.get_user_playlists()

    # Get playlists from our database
    statement = select(Playlist).where(Playlist.user_id == user_id)
    db_playlists = db.exec(statement).all()

    # Merge and deduplicate playlists
    playlist_map = {p["id"]: p for p in spotify_playlists}
    for db_playlist in db_playlists:
        if str(db_playlist.id) not in playlist_map:
            playlist_map[str(db_playlist.id)] = db_playlist.to_response()

    return list(playlist_map.values())


async def get_user_mutual_playlists(
    user1_id: UUID, user2_id: UUID, db: Session
) -> List[PlaylistResponse]:
    """Get mutual playlists between two users"""
    # Get both users' playlists from Spotify
    user1_spotify = await get_spotify_client(user1_id, db)
    user2_spotify = await get_spotify_client(user2_id, db)

    # Get playlists for both users
    user1_playlists = await user1_spotify.get_user_playlists()
    user2_playlists = await user2_spotify.get_user_playlists()

    # Find mutual playlists (playlists that both users follow)
    user1_playlist_ids = {p["id"] for p in user1_playlists}
    user2_playlist_ids = {p["id"] for p in user2_playlists}
    mutual_ids = user1_playlist_ids.intersection(user2_playlist_ids)

    # Get mutual playlists from our database
    statement = select(Playlist).where(
        (Playlist.user_id.in_([user1_id, user2_id]))
        & (Playlist.id.in_([UUID(pid) for pid in mutual_ids]))
    )
    db_playlists = db.exec(statement).all()

    # Merge Spotify and database playlists
    mutual_playlists = [p for p in user1_playlists if p["id"] in mutual_ids]
    for db_playlist in db_playlists:
        if str(db_playlist.id) not in {p["id"] for p in mutual_playlists}:
            mutual_playlists.append(db_playlist.to_response())

    return mutual_playlists


async def create_user_playlist(
    user_id: UUID, playlist_data: PlaylistCreate, db: Session
) -> PlaylistResponse:
    """Create a new playlist in both Spotify and our database"""
    # TODO:  add error handling
    # TODO:  There should be a limit on tracks to be added to a playlist
    # TODO:  This should be  self generating playlist based on users taste
    spotify = await get_spotify_client(user_id, db)
    spotify_playlist = await spotify.create_playlist(
        name=playlist_data.name,
        description=playlist_data.description,
        public=playlist_data.public,
    )

    # Add tracks if provided
    if playlist_data.tracks:
        if len(playlist_data.tracks) > 100:
            raise HTTPException(
                status_code=400, detail="Cannot add more than 100 tracks at once"
            )
        await spotify.add_tracks_to_playlist(
            playlist_id=spotify_playlist["id"], track_uris=playlist_data.tracks
        )

    # Create playlist in our database
    db_playlist = Playlist(
        id=UUID(spotify_playlist["id"]),
        user_id=user_id,
        name=playlist_data.name,
        description=playlist_data.description,
        public=playlist_data.public,
        spotify_id=spotify_playlist["id"],
        tracks=playlist_data.tracks or [],
    )
    db.add(db_playlist)
    db.commit()
    db.refresh(db_playlist)

    return spotify_playlist


async def update_user_playlist(
    playlist_id: UUID, playlist_update: PlaylistUpdate, db: Session
) -> PlaylistResponse:
    """Update a playlist in both Spotify and our database"""
    # Get playlist from database
    statement = select(Playlist).where(Playlist.id == playlist_id)
    playlist = db.exec(statement).first()
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    # Update playlist in Spotify
    spotify = await get_spotify_client(playlist.user_id, db)
    spotify_playlist = await spotify.update_playlist(
        playlist_id=str(playlist_id),
        name=playlist_update.name,
        description=playlist_update.description,
        public=playlist_update.public,
    )

    # Update tracks if provided
    if playlist_update.tracks is not None:
        # Add new tracks
        if playlist_update.tracks:
            if len(playlist_update.tracks) > 100:
                raise HTTPException(
                    status_code=400, detail="Cannot add more than 100 tracks at once"
                )
            await spotify.add_tracks_to_playlist(
                playlist_id=str(playlist_id), track_uris=playlist_update.tracks
            )

    # Update playlist in database
    playlist.name = playlist_update.name or playlist.name
    playlist.description = playlist_update.description or playlist.description
    playlist.public = (
        playlist_update.public
        if playlist_update.public is not None
        else playlist.public
    )
    playlist.tracks = playlist_update.tracks or playlist.tracks

    db.add(playlist)
    db.commit()
    db.refresh(playlist)

    return spotify_playlist
