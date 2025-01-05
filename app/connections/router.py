from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database.database import get_db
from app.auth.auth import get_authenticated_user
from app.models.models import User, Connection
from app.recommendation.music_recommender import MusicRecommender

from .connections import (
    get_user_connections,
    create_connection,
    accept_connection,
    reject_connection,
    delete_connection,
)

router = APIRouter()
recommender = MusicRecommender()


@router.get("/connections", response_model=List[Connection])
async def list_user_connections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
) -> List[Connection]:
    """Get all connections for the current user"""
    return get_user_connections(db, current_user.id)


@router.post("/request/{target_user_id}")
async def request_connection(
    target_user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    """Create a connection request"""
    connection = create_connection(db, current_user.id, target_user_id)
    return {"message": "Connection request sent", "connection": connection}


@router.post("/accept/{connection_id}")
async def accept_connection_request(
    connection_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    """Accept a connection request"""
    connection = accept_connection(db, connection_id)
    return {"message": "Connection accepted", "connection": connection}


@router.post("/reject/{connection_id}")
async def reject_connection_request(
    connection_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    """Reject a connection request"""
    connection = reject_connection(db, connection_id)
    return {"message": "Connection rejected", "connection": connection}


@router.delete("/{connection_id}")
async def remove_connection(
    connection_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_authenticated_user),
):
    """Remove an existing connection"""
    result = delete_connection(db, connection_id)
    return {"message": "Connection deleted"}
