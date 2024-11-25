from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.datamodels import User, MusicProfile
from app.models.schema import (
    Artist, TopArtistsResponse, TopGenresResponse,
    MutualMusicInterests, MusicRecommendationsResponse,
    TrackRecommendation
)
from app.helpers.spotify import get_spotify_client

async def get_user_top_artists(
    db: Session,
    user_id: str,
    time_range: str = "medium_term",
    limit: int = 20
) -> TopArtistsResponse:
    """Get user's top artists from Spotify"""
    spotify = await get_spotify_client(user_id, db)
    
    try:
        top_artists = await spotify.current_user_top_artists(
            limit=limit,
            time_range=time_range
        )
        
        artists = [
            Artist(
                id=artist["id"],
                name=artist["name"],
                genres=artist["genres"],
                popularity=artist["popularity"],
                image_url=artist["images"][0]["url"] if artist["images"] else None
            )
            for artist in top_artists["items"]
        ]
        
        return TopArtistsResponse(
            items=artists,
            total=len(artists),
            time_range=time_range
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching top artists: {str(e)}"
        )

async def get_user_top_genres(
    db: Session,
    user_id: str,
    time_range: str = "medium_term"
) -> TopGenresResponse:
    """Get user's top genres based on their top artists"""
    spotify = await get_spotify_client(user_id, db)
    
    try:
        top_artists = await spotify.current_user_top_artists(
            time_range=time_range
        )
        
        # Collect all genres from top artists
        all_genres = []
        for artist in top_artists["items"]:
            all_genres.extend(artist["genres"])
        
        # Count genre occurrences and sort by frequency
        genre_count = {}
        for genre in all_genres:
            genre_count[genre] = genre_count.get(genre, 0) + 1
        
        sorted_genres = sorted(
            genre_count.keys(),
            key=lambda x: genre_count[x],
            reverse=True
        )
        
        return TopGenresResponse(
            genres=sorted_genres,
            time_range=time_range
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching top genres: {str(e)}"
        )

async def get_music_recommendations(
    db: Session,
    user_id: str,
    limit: int = 20
) -> MusicRecommendationsResponse:
    """Get personalized music recommendations"""
    spotify = await get_spotify_client(user_id, db)
    
    try:
        # Get user's top artists and genres for seeds
        top_artists = await spotify.current_user_top_artists(limit=5)
        artist_ids = [artist["id"] for artist in top_artists["items"][:2]]
        
        # Get genres from top artists
        all_genres = []
        for artist in top_artists["items"]:
            all_genres.extend(artist["genres"])
        unique_genres = list(set(all_genres))[:3]
        
        # Get recommendations
        recommendations = await spotify.recommendations(
            seed_artists=artist_ids,
            seed_genres=unique_genres,
            limit=limit
        )
        
        tracks = [
            TrackRecommendation(
                id=track["id"],
                name=track["name"],
                artist=track["artists"][0]["name"],
                album=track["album"]["name"],
                preview_url=track["preview_url"],
                image_url=track["album"]["images"][0]["url"] if track["album"]["images"] else None
            )
            for track in recommendations["tracks"]
        ]
        
        return MusicRecommendationsResponse(
            tracks=tracks,
            seed_artists=[artist["name"] for artist in top_artists["items"][:2]],
            seed_genres=unique_genres
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching recommendations: {str(e)}"
        )

async def get_mutual_music_interests(
    db: Session,
    user_id: str,
    other_user_id: str
) -> MutualMusicInterests:
    """Get mutual music interests between two users"""
    spotify = await get_spotify_client(user_id, db)
    other_spotify = await get_spotify_client(other_user_id, db)
    
    try:
        # Get both users' top artists
        user_artists_resp = await spotify.current_user_top_artists()
        other_artists_resp = await other_spotify.current_user_top_artists()
        
        # Convert responses to Artist objects
        user_artists = [
            Artist(
                id=artist["id"],
                name=artist["name"],
                genres=artist["genres"],
                popularity=artist["popularity"],
                image_url=artist["images"][0]["url"] if artist["images"] else None
            )
            for artist in user_artists_resp["items"]
        ]
        
        other_artists = [
            Artist(
                id=artist["id"],
                name=artist["name"],
                genres=artist["genres"],
                popularity=artist["popularity"],
                image_url=artist["images"][0]["url"] if artist["images"] else None
            )
            for artist in other_artists_resp["items"]
        ]
        
        # Find mutual artists
        user_artist_ids = {artist.id for artist in user_artists}
        mutual_artists = [
            artist for artist in other_artists
            if artist.id in user_artist_ids
        ]
        
        # Get all genres
        user_genres = set()
        other_genres = set()
        
        for artist in user_artists:
            user_genres.update(artist.genres)
        for artist in other_artists:
            other_genres.update(artist.genres)
        
        # Find mutual genres
        mutual_genres = list(user_genres.intersection(other_genres))
        
        # Calculate compatibility score
        total_items = len(user_artists) + len(user_genres)
        mutual_items = len(mutual_artists) + len(mutual_genres)
        compatibility_score = (mutual_items / total_items) * 100 if total_items > 0 else 0
        
        return MutualMusicInterests(
            mutual_artists=mutual_artists,
            mutual_genres=mutual_genres,
            compatibility_score=round(compatibility_score, 2)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating mutual interests: {str(e)}"
        )
