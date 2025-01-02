from typing import List, Dict, Any

import httpx
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.database.database import get_db
from app.users.users import get_user_by_token, update_user_profile, get_user
from app.constant import API_BASE_URL
from app.auth.auth import get_header

from app.models.models import MusicProfile
from app.music.profile_analyzer import MusicProfileAnalyzer
from app.models.schema import Metrics


class SpotifyClient:
    """Spotify API client for making authenticated requests"""

    def __init__(self, token: str):
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"}

    async def current_user_top_artists(
        self, limit: int = 20, time_range: str = "medium_term"
    ) -> Dict[str, Any]:
        """Get the current user's top artists"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}me/top/artists",
                headers=self.headers,
                params={"limit": limit, "time_range": time_range},
            )
            response.raise_for_status()
            return response.json()

    async def current_user_top_tracks(
        self, limit: int = 20, time_range: str = "medium_term"
    ) -> Dict[str, Any]:
        """Get the current user's top tracks"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}me/top/tracks",
                headers=self.headers,
                params={"limit": limit, "time_range": time_range},
            )
            response.raise_for_status()
            return response.json()

    async def recommendations(
        self,
        seed_artists: List[str] = None,
        seed_genres: List[str] = None,
        seed_tracks: List[str] = None,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """Get track recommendations based on seeds"""
        params = {"limit": limit}
        if seed_artists:
            params["seed_artists"] = ",".join(seed_artists[:2])
        if seed_genres:
            params["seed_genres"] = ",".join(seed_genres[:3])
        if seed_tracks:
            params["seed_tracks"] = ",".join(seed_tracks[:2])

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}recommendations", headers=self.headers, params=params
            )
            response.raise_for_status()
            return response.json()

    async def get_artist(self, artist_id: str) -> Dict[str, Any]:
        """Get Spotify catalog information for an artist"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}artists/{artist_id}", headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def get_user_data(self) -> Dict[str, Any]:
        """Get the current user's Spotify profile"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}me", headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def current_user_recently_played(self, limit: int = 50) -> Dict[str, Any]:
        """Get the current user's recently played tracks

        Args:
            limit: The maximum number of items to return (max: 50)

        Returns:
            A dictionary containing the recently played tracks
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}me/player/recently-played",
                headers=self.headers,
                params={
                    "limit": min(limit, 50)
                },  # Ensure limit doesn't exceed Spotify's max
            )
            response.raise_for_status()
            return response.json()

    async def create_playlist(
        self, user_id: str, name: str, description: str = None, public: bool = True
    ) -> Dict[str, Any]:
        """Create a new playlist in Spotify"""
        data = {"name": name, "public": public, "description": description}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}users/{user_id}/playlists",
                headers=self.headers,
                json=data,
            )
            response.raise_for_status()
            return response.json()

    async def update_playlist(
        self,
        playlist_id: str,
        name: str = None,
        description: str = None,
        public: bool = None,
    ) -> Dict[str, Any]:
        """Update an existing Spotify playlist"""
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
                headers=self.headers,
                json=data,
            )
            response.raise_for_status()
            return response.json()

    async def delete_playlist(self, playlist_id: str):
        """Delete a Spotify playlist"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{API_BASE_URL}playlists/{playlist_id}/followers", headers=self.headers
            )
            response.raise_for_status()

    async def add_tracks_to_playlist(self, playlist_id: str, track_uris: List[str]):
        """Add tracks to a Spotify playlist"""
        data = {"uris": track_uris}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}playlists/{playlist_id}/tracks",
                headers=self.headers,
                json=data,
            )
            response.raise_for_status()

    async def clear_playlist(self, playlist_id: str):
        """Remove all tracks from a Spotify playlist"""
        async with httpx.AsyncClient() as client:
            # First, get all tracks in the playlist
            tracks_response = await client.get(
                f"{API_BASE_URL}playlists/{playlist_id}/tracks", headers=self.headers
            )
            tracks_response.raise_for_status()
            tracks = tracks_response.json()["items"]

            # Create list of track URIs to remove
            tracks_to_remove = [{"uri": track["track"]["uri"]} for track in tracks]

            if tracks_to_remove:
                # Remove all tracks
                response = await client.delete(
                    f"{API_BASE_URL}playlists/{playlist_id}/tracks",
                    headers=self.headers,
                    json={"tracks": tracks_to_remove},
                )
                response.raise_for_status()

    async def get_playlist_tracks(self, playlist_id: str) -> List[str]:
        """Get all track URIs from a playlist"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}playlists/{playlist_id}/tracks", headers=self.headers
            )
            response.raise_for_status()
            tracks = response.json()["items"]
            return [track["track"]["uri"] for track in tracks]

    async def audio_features(self, track_ids: List[str]) -> List[Dict[str, Any]]:
        """Get audio features for a list of tracks"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}audio-features",
                headers=self.headers,
                params={"ids": ",".join(track_ids)},
            )
            response.raise_for_status()
            return response.json()["audio_features"]


async def get_spotify_client(
    user_id: str, db: Session = Depends(get_db)
) -> SpotifyClient:
    """Get a configured Spotify client for a user"""
    # Get the user's access token from the database
    user = await get_user(db, user_id)
    if not user or not user.spotify_token:
        raise HTTPException(
            status_code=401, detail="User not found or Spotify token not available"
        )

    return SpotifyClient(user.spotify_token)


async def sync_user_spotify_data(user_id: str, db: Session) -> None:
    """
    Sync user's Spotify data with our database.
    This includes:
    - User profile (spotify_id, display_name, etc.)
    - Music profile (top artists, tracks, genres, etc.)
    """
    spotify = await get_spotify_client(user_id, db)
    analyzer = MusicProfileAnalyzer(spotify)

    try:
        # Get user profile data
        user_data = await spotify.get_user_data()

        # Get top artists and tracks data
        top_tracks_data = await spotify.current_user_top_tracks(
            limit=50, time_range="long_term"
        )
        top_artists_data = await spotify.current_user_top_artists(
            limit=50, time_range="long_term"
        )

        # Extract core music data
        top_artists = [
            {
                "name": artist["name"],
                "id": artist["id"],
                "popularity": artist["popularity"],
                "genres": artist["genres"],
            }
            for artist in top_artists_data["items"]
        ]

        top_tracks = [
            {
                "name": track["name"],
                "id": track["id"],
                "artist": track["artists"][0]["name"],
                "album": track["album"]["name"],
                "popularity": track["popularity"],
            }
            for track in top_tracks_data["items"]
        ]

        genres = list(
            set(
                [
                    genre
                    for artist in top_artists_data["items"]
                    for genre in artist.get("genres", [])
                ]
            )
        )

        # Update user data
        user_update = {
            "spotify_id": user_data["id"],
            "display_name": user_data["display_name"],
            "spotify_url": user_data["external_urls"]["spotify"],
            "spotify_image_url": (
                user_data["images"][0]["url"] if user_data.get("images") else None
            ),
            "country": user_data.get("country"),
            "last_spotify_sync": datetime.utcnow(),
        }
        await update_user(db, user_id, **user_update)

        # Calculate all profile metrics
        profile_metrics: Metrics = await analyzer.get_complete_profile_metrics()

        # Get or create music profile
        music_profile = (
            db.query(MusicProfile).filter(MusicProfile.user_id == user_id).first()
        )
        if not music_profile:
            music_profile = MusicProfile(user_id=user_id)
            db.add(music_profile)

        # Update music profile with core data and metrics
        music_profile.top_artists = top_artists
        music_profile.top_tracks = top_tracks
        music_profile.genres = genres
        music_profile.favorite_decades = profile_metrics.favorite_decades
        music_profile.energy_score = profile_metrics.energy_score
        music_profile.danceability_score = profile_metrics.danceability_score
        music_profile.diversity_score = profile_metrics.diversity_score
        music_profile.obscurity_score = profile_metrics.obscurity_score
        music_profile.listening_history = profile_metrics.listening_patterns
        music_profile.updated_at = datetime.utcnow()

        # Commit all changes
        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to sync Spotify data: {str(e)}"
        )
