from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, select, and_

from app.recommendation.music_recommender import MusicRecommender
from app.models.models import Connection, MusicProfile


recommender = MusicRecommender()


def get_user_connections(db: Session, user_id: UUID) -> List[Connection]:
    """Get connections for a user"""
    statement = select(Connection).where(Connection.user_id == user_id)
    return db.exec(statement).all()


def create_connection(db: Session, user_id: UUID, target_user_id: UUID) -> Connection:
    """Create a connection between two users"""
    # Check if connection already exists
    statement = select(Connection).where(
        and_(
            Connection.user_id == user_id,
            Connection.connected_user_id == target_user_id,
        )
    )
    existing = db.exec(statement).first()
    if existing:
        raise HTTPException(status_code=400, detail="Connection already exists")

    # Get both users' music profiles
    user_profile_statement = select(MusicProfile).where(MusicProfile.user_id == user_id)
    target_profile_statement = select(MusicProfile).where(
        MusicProfile.user_id == target_user_id
    )

    current_profile = db.exec(user_profile_statement).first()
    target_profile = db.exec(target_profile_statement).first()

    if not current_profile or not target_profile:
        raise HTTPException(status_code=404, detail="Music profile not found")

    # TODO: : we probably don't need to calculate compatability at this point
    # we are alreadysending compatability when recommending users in `/recommendations/users` endpoint
    # Calculate compatibility score
    current_profile_dict = current_profile.dict()
    target_profile_dict = target_profile.dict()
    compatibility = recommender.calculate_overall_similarity(
        current_profile_dict, target_profile_dict
    )

    # Find shared music elements
    shared_genres = list(set(current_profile.genres) & set(target_profile.genres))
    shared_artists = list(
        set(current_profile.top_artists) & set(target_profile.top_artists)
    )
    shared_tracks = list(
        set(current_profile.top_tracks) & set(target_profile.top_tracks)
    )

    # Create new connection
    new_connection = Connection(
        user_id=user_id,
        connected_user_id=target_user_id,
        status="pending",
        overall_compatibility=int(compatibility.overall_similarity * 100),
        compatibility_breakdown=compatibility.dict(),
        shared_genres=shared_genres,
        shared_artists=shared_artists,
        shared_tracks=shared_tracks,
    )

    # Add connection to database
    db.add(new_connection)
    db.commit()
    db.refresh(new_connection)
    return new_connection


def accept_connection(db: Session, connection_id: UUID) -> Connection:
    """Accept a connection request"""
    statement = select(Connection).where(Connection.id == connection_id)
    connection = db.exec(statement).first()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    connection.status = "accepted"
    db.add(connection)
    db.commit()
    db.refresh(connection)
    return connection


def reject_connection(db: Session, connection_id: UUID) -> Connection:
    """Reject a connection request"""
    statement = select(Connection).where(Connection.id == connection_id)
    connection = db.exec(statement).first()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    connection.status = "rejected"
    db.add(connection)
    db.commit()
    db.refresh(connection)
    return connection


def delete_connection(db: Session, connection_id: UUID) -> None:
    """Delete a connection"""
    statement = select(Connection).where(Connection.id == connection_id)
    connection = db.exec(statement).first()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    db.delete(connection)
    db.commit()
    return {"message": "Connection deleted"}
