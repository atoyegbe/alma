from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.recommendation.music_recommender import MusicRecommender
from app.models.datamodels import Connection


recommender = MusicRecommender()

def get_user_connections(db: Session, user_id: int) -> List[Connection]:
    """Get connections for a user"""
    return db.query(Connection).filter(Connection.user_id == user_id).all()

def create_connection(db: Session, user_id: int, target_user_id: int) -> Connection:
    """Create a connection between two users"""
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
    
    # TODO: : we probably don't need to calculate compatability at this point
    # we are alreadysending compatability when recommending users in `/recommendations/users` endpoint
    # Calculate compatibility score
    current_profile = current_profile.to_dict()
    target_profile = target_profile.to_dict()
    compatibility_score = recommender.calculate_overall_similarity(current_profile, target_profile)
    
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
    
    # Add connection to database
    db.add(new_connection)
    db.commit()
    db.refresh(new_connection)
    return new_connection

def accept_connection(db: Session, connection_id: int) -> Connection:
    """Accept a connection request"""
    connection = db.query(Connection).filter(Connection.id == connection_id).first()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    connection.status = "accepted"
    db.commit()
    db.refresh(connection)
    return connection

def reject_connection(db: Session, connection_id: int) -> Connection:
    """Reject a connection request"""
    connection = db.query(Connection).filter(Connection.id == connection_id).first()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    connection.status = "rejected"
    db.commit()
    db.refresh(connection)
    return connection

def delete_connection(db: Session, connection_id: int) -> Connection:
    """Delete a connection"""
    connection = db.query(Connection).filter(Connection.id == connection_id).first()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    db.delete(connection)
    db.commit()
    return {"message": "Connection deleted"}
