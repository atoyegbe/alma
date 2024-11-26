from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import db_dependency
from app.auth.auth import get_current_user
from app.models.datamodels import User, Connection, MusicProfile
from app.recommendation.music_recommender import MusicRecommender

from .connections import get_user_connections, create_connection

router = APIRouter()
recommender = MusicRecommender()


@router.get("/connections", response_model=List[Connection])
async def get_user_connections(
    db: db_dependency,
    current_user: User = Depends(get_current_user),
) -> List[Connection]:
    """Get all connections for the current user"""
    return get_user_connections(db, current_user.id)

@router.post("/request/{target_user_id}")
async def create_connection(
    target_user_id: str,
    db: db_dependency,
    current_user: User = Depends(get_current_user),
):
    """Create a connection request"""

    create_connection(db, current_user.id, target_user_id)
    return {"message": "Connection request sent"}

@router.post("/accept/{connection_id}")
async def accept_connection(
    connection_id: str,
    db: db_dependency,
    current_user: User = Depends(get_current_user),
):
    """Accept a connection request"""
    return accept_connection(db, connection_id)

@router.post("/reject/{connection_id}")
async def reject_connection(
    connection_id: str,
    db: db_dependency,
    current_user: User = Depends(get_current_user),
):
    """Reject a connection request"""
    return reject_connection(db, connection_id)

@router.delete("/{connection_id}")
async def delete_connection(
    connection_id: str,
    db: db_dependency,

    current_user: User = Depends(get_current_user),
):
    return delete_connection(db, connection_id)
