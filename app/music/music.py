from typing import List, Optional
from uuid import UUID
from collections import Counter

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.models import User, MusicProfile
from app.models.schema import (
    Artist, TopArtistsResponse, TopGenresResponse,
    MutualMusicInterests, MusicRecommendationsResponse,
    TrackRecommendation
)
from app.helpers.spotify import get_spotify_client

async def get_user_top_artists(
    db: Session,
    user_id: UUID,
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
    user_id: UUID,
    time_range: str = "medium_term"
) -> TopGenresResponse:
    """Get user's top genres based on their top artists"""
    spotify = await get_spotify_client(user_id, db)
    
    try:
        top_artists = await spotify.current_user_top_artists(
            limit=50,  # Get more artists for better genre analysis
            time_range=time_range
        )
        
        # Extract and count genres
        all_genres = []
        for artist in top_artists["items"]:
            all_genres.extend(artist["genres"])
        
        # Count genre occurrences and sort by frequency
        
        genre_counts = Counter(all_genres)
        top_genres = [genre for genre, _ in genre_counts.most_common(20)]
        
        return TopGenresResponse(
            genres=top_genres,
            time_range=time_range
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching top genres: {str(e)}"
        )

async def get_music_recommendations(
    db: Session,
    user_id: UUID,
    limit: int = 20
) -> MusicRecommendationsResponse:
    """Get personalized music recommendations"""
    spotify = await get_spotify_client(user_id, db)
    
    try:
        # Get user's top artists and genres
        top_artists_resp = await get_user_top_artists(db, user_id, limit=5)
        top_genres_resp = await get_user_top_genres(db, user_id)
        
        seed_artists = [artist.id for artist in top_artists_resp.items[:2]]
        seed_genres = top_genres_resp.genres[:3]
        
        # Get recommendations from Spotify
        recommendations = await spotify.recommendations(
            seed_artists=seed_artists,
            seed_genres=seed_genres,
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
            seed_artists=seed_artists,
            seed_genres=seed_genres
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting recommendations: {str(e)}"
        )

async def get_mutual_music_interests(
    db: Session,
    user1_id: UUID,
    user2_id: UUID
) -> MutualMusicInterests:
    """Get mutual music interests between two users"""
    # Get both users' profiles
    statement1 = select(MusicProfile).where(MusicProfile.user_id == user1_id)
    statement2 = select(MusicProfile).where(MusicProfile.user_id == user2_id)
    
    profile1 = db.exec(statement1).first()
    profile2 = db.exec(statement2).first()
    
    if not profile1 or not profile2:
        raise HTTPException(status_code=404, detail="One or both user profiles not found")
    
    # Find mutual artists
    mutual_artists = []
    if profile1.top_artists and profile2.top_artists:
        artists1 = {artist["id"]: artist for artist in profile1.top_artists}
        artists2 = {artist["id"]: artist for artist in profile2.top_artists}
        
        mutual_artist_ids = set(artists1.keys()) & set(artists2.keys())
        mutual_artists = [
            Artist(
                id=artist_id,
                name=artists1[artist_id]["name"],
                genres=artists1[artist_id]["genres"],
                popularity=artists1[artist_id]["popularity"],
                image_url=artists1[artist_id].get("image_url")
            )
            for artist_id in mutual_artist_ids
        ]
    
    # Find mutual genres
    mutual_genres = []
    if profile1.genres and profile2.genres:
        mutual_genres = list(set(profile1.genres) & set(profile2.genres))
    
    # Calculate compatibility score based on mutual interests
    total_score = 0.0
    if mutual_artists:
        total_score += len(mutual_artists) * 0.6  # Weight artist matches more heavily
    if mutual_genres:
        total_score += len(mutual_genres) * 0.4
    
    # Normalize score to 0-100 range
    compatibility_score = min(100, total_score * 10)
    
    return MutualMusicInterests(
        mutual_artists=mutual_artists,
        mutual_genres=mutual_genres,
        compatibility_score=compatibility_score
    )

async def sync_user_spotify_data(user_id: UUID, db: Session):
    """Sync user's Spotify data with our database"""
    # Get user's profile
    statement = select(MusicProfile).where(MusicProfile.user_id == user_id)
    profile = db.exec(statement).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    try:
        # Get user's top artists and genres
        top_artists = await get_user_top_artists(db, user_id, limit=50)
        top_genres = await get_user_top_genres(db, user_id)
        
        # Update profile with new data
        profile.top_artists = [artist.model_dump() for artist in top_artists.items]
        profile.genres = top_genres.genres
        
        # Save changes
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error syncing Spotify data: {str(e)}"
        )
