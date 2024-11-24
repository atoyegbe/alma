import httpx
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.user import get_user_by_token, update_user
from app.main import app
from app.constant import API_BASE_URL
from app.auth.auth import get_header
from typing import List, Dict, Any

async def get_followed_artist(token: str):
    try:
        response = await app.state.http_client.get(
            f"{API_BASE_URL}me/following?type=artist", headers=get_header(token)
        )
        artists = response.json()
        return artists
    except httpx.RequestError as e:
        raise HTTPException(status_code=400, detail=f"Request error: {str(e)}")


async def save_top_artists(token: str, db: Session = Depends(get_db)):
    response = await app.state.http_client.get(
        f"{API_BASE_URL}me/top/artists?time_range=long_term", headers=get_header(token)
    )
    resp = response.json()
    top_artists = [track["name"] for track in resp["items"]]
    genres_list = [track["genres"] for track in resp["items"] if track["genres"]]
    flattened_list = [genre for genres in genres_list for genre in genres]

    print("saving user genres and top artists")
    current_user = await get_user_by_token(db, token)
    await update_user(
        db,
        current_user.user_id,
        **{"top_artists": top_artists, "genres": list(set(flattened_list))},
    )


async def save_user_top_tracks(token: str, db: Session = Depends(get_db)):
    response = await app.state.http_client.get(
        f"{API_BASE_URL}me/top/tracks?time_range=long_term", headers=get_header(token)
    )
    resp = response.json()
    top_tracks = [track["name"] for track in resp["items"]]
    current_user = await get_user_by_token(db, token)
    await update_user(db, current_user.user_id, **{"top_tracks": top_tracks})


async def get_spotify_user_data(access_token: str) -> dict:
    headers = {"Authorization": f"Bearer {access_token}"}

    response = await app.state.http_client.get(
        "https://api.spotify.com/v1/me", headers=headers
    )
    return response.json()


async def create_spotify_playlist(
    user_id: str,
    token: str,
    name: str,
    description: str = None,
    public: bool = True
) -> Dict[str, Any]:
    """Create a new playlist in Spotify"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": name,
        "public": public,
        "description": description
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}users/{user_id}/playlists",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()

async def update_spotify_playlist(
    playlist_id: str,
    token: str,
    name: str = None,
    description: str = None,
    public: bool = None
) -> Dict[str, Any]:
    """Update an existing Spotify playlist"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {}
    if name is not None:
        data["name"] = name
    if description is not None:
        data["description"] = description
    if public is not None:
        data["public"] = public
    
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{API_BASE_URL}playlists/{playlist_id}",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()

async def delete_spotify_playlist(playlist_id: str, token: str):
    """Delete a Spotify playlist"""
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{API_BASE_URL}playlists/{playlist_id}/followers",
            headers=headers
        )
        response.raise_for_status()

async def add_tracks_to_playlist(
    playlist_id: str,
    track_uris: List[str],
    token: str
):
    """Add tracks to a Spotify playlist"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {"uris": track_uris}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}playlists/{playlist_id}/tracks",
            headers=headers,
            json=data
        )
        response.raise_for_status()

async def clear_playlist_tracks(playlist_id: str, token: str):
    """Remove all tracks from a Spotify playlist"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # First, get all tracks in the playlist
    async with httpx.AsyncClient() as client:
        tracks_response = await client.get(
            f"{API_BASE_URL}playlists/{playlist_id}/tracks",
            headers=headers
        )
        tracks_response.raise_for_status()
        tracks = tracks_response.json()["items"]
        
        # Create list of track URIs to remove
        tracks_to_remove = [{"uri": track["track"]["uri"]} for track in tracks]
        
        if tracks_to_remove:
            # Remove all tracks
            response = await client.delete(
                f"{API_BASE_URL}playlists/{playlist_id}/tracks",
                headers=headers,
                json={"tracks": tracks_to_remove}
            )
            response.raise_for_status()

async def get_playlist_tracks(playlist_id: str, token: str) -> List[str]:
    """Get all track URIs from a playlist"""
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_BASE_URL}playlists/{playlist_id}/tracks",
            headers=headers
        )
        response.raise_for_status()
        tracks = response.json()["items"]
        return [track["track"]["uri"] for track in tracks]
