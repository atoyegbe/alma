from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database.database import db_dependency
from app.auth.auth import get_current_user
from app.models.datamodels import User, Connection, MusicProfile
from app.recommendation.music_recommender import MusicRecommender

router = APIRouter()
recommender = MusicRecommender()

@router.get("/connections")
async def get_user_connections(
    db: db_dependency,
    current_user: User = Depends(get_current_user),
) -> List[dict]:
    """Get all connections for the current user"""
    connections = db.query(Connection).filter(
        Connection.user_id == current_user.id
    ).all()
    
    return connections

@router.post("/request/{target_user_id}")
async def create_connection(
    target_user_id: str,
    db: db_dependency,
    current_user: User = Depends(get_current_user),
    
):
    """Create a new connection request with compatibility calculation"""
    # Check if connection already exists
    existing = db.query(Connection).filter(
        and_(
            Connection.user_id == current_user.id,
            Connection.connected_user_id == target_user_id
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Connection already exists")
    
    # Get both users' music profiles
    current_profile = db.query(MusicProfile).filter(
        MusicProfile.user_id == current_user.id
    ).first()
    target_profile = db.query(MusicProfile).filter(
        MusicProfile.user_id == target_user_id
    ).first()
    
    if not current_profile or not target_profile:
        raise HTTPException(status_code=404, detail="Music profile not found")
    
    # Calculate compatibility
    profile1 = {
        "id": current_user.id,
        "genres": current_profile.genres,
        "top_artists": current_profile.top_artists,
        "top_tracks": current_profile.top_tracks,
        "favorite_decades": current_profile.favorite_decades,
        "energy_score": current_profile.energy_score,
        "danceability_score": current_profile.danceability_score,
        "diversity_score": current_profile.diversity_score,
        "obscurity_score": current_profile.obscurity_score,
        "listening_history": current_profile.listening_history
    }
    
    profile2 = {
        "id": target_user_id,
        "genres": target_profile.genres,
        "top_artists": target_profile.top_artists,
        "top_tracks": target_profile.top_tracks,
        "favorite_decades": target_profile.favorite_decades,
        "energy_score": target_profile.energy_score,
        "danceability_score": target_profile.danceability_score,
        "diversity_score": target_profile.diversity_score,
        "obscurity_score": target_profile.obscurity_score,
        "listening_history": target_profile.listening_history
    }
    
    compatibility = recommender.calculate_overall_similarity(profile1, profile2)
    
    # Find shared music elements
    shared_genres = list(set(current_profile.genres) & set(target_profile.genres))
    shared_artists = list(set(a["id"] for a in current_profile.top_artists) & 
                         set(a["id"] for a in target_profile.top_artists))
    shared_tracks = list(set(t["id"] for t in current_profile.top_tracks) & 
                        set(t["id"] for t in target_profile.top_tracks))
    
    # Create new connection
    new_connection = Connection(
        user_id=current_user.id,
        connected_user_id=target_user_id,
        status="pending",
        overall_compatibility=int(compatibility["overall_similarity"] * 100),
        compatibility_breakdown=compatibility["component_similarities"],
        shared_genres=shared_genres,
        shared_artists=shared_artists,
        shared_tracks=shared_tracks
    )
    
    db.add(new_connection)
    db.commit()
    db.refresh(new_connection)
    
    return new_connection

@router.post("/accept/{connection_id}")
async def accept_connection(
    connection_id: str,
    db: db_dependency,
    current_user: User = Depends(get_current_user),
):
    """Accept a connection request"""
    connection = db.query(Connection).filter(
        and_(
            Connection.id == connection_id,
            Connection.connected_user_id == current_user.id,
            Connection.status == "pending"
        )
    ).first()
    
    if not connection:
        raise HTTPException(status_code=404, detail="Connection request not found")
    
    connection.status = "accepted"
    db.commit()
    
    return connection

@router.post("/reject/{connection_id}")
async def reject_connection(
    connection_id: str,
    db: db_dependency,
    current_user: User = Depends(get_current_user),
):
    """Reject a connection request"""
    connection = db.query(Connection).filter(
        and_(
            Connection.id == connection_id,
            Connection.connected_user_id == current_user.id,
            Connection.status == "pending"
        )
    ).first()
    
    if not connection:
        raise HTTPException(status_code=404, detail="Connection request not found")
    
    connection.status = "rejected"
    db.commit()
    
    return connection

@router.delete("/{connection_id}")
async def delete_connection(
    connection_id: str,
    db: db_dependency,

    current_user: User = Depends(get_current_user),
):
    """Delete a connection"""
    connection = db.query(Connection).filter(
        and_(
            Connection.id == connection_id,
            Connection.user_id == current_user.id
        )
    ).first()
    
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    db.delete(connection)
    db.commit()
    
    return {"message": "Connection deleted"}
