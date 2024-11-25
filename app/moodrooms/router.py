from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.auth.auth import get_current_user
from app.database.database import db_dependency
from app.models.datamodels import MoodRoom
from app.models.schema import MoodRoomResponse, MoodRoomCreate, UserResponse

router = APIRouter()

@router.get("/", response_model=List[MoodRoomResponse])
async def list_mood_rooms(
    db: db_dependency,
    current_user: UserResponse = Depends(get_current_user)
):
    """List all available mood rooms"""
    rooms = db.query(MoodRoom).all()
    return rooms

@router.get("/{room_id}", response_model=MoodRoomResponse)
async def get_room_details(
    room_id: UUID,
    db: db_dependency,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get details of a specific mood room"""
    room = db.query(MoodRoom).filter(MoodRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Mood room not found")
    return room

@router.post("/join/{room_id}")
async def join_room(
    room_id: UUID,
    db: db_dependency,
    current_user: UserResponse = Depends(get_current_user)
):
    """Join a mood room"""
    room = db.query(MoodRoom).filter(MoodRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Mood room not found")
    
    # Logic to add user to room participants
    # This will depend on how you're tracking room participants
    # You might want to create a room_participants table
    
    return {"message": "Successfully joined the room"}

@router.post("/leave/{room_id}")
async def leave_room(
    room_id: UUID,
    db: db_dependency,
    current_user: UserResponse = Depends(get_current_user)
):
    """Leave a mood room"""
    room = db.query(MoodRoom).filter(MoodRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Mood room not found")
    
    # Logic to remove user from room participants
    
    return {"message": "Successfully left the room"}

@router.get("/{room_id}/users", response_model=List[UserResponse])
async def get_room_users(
    room_id: UUID,
    db: db_dependency,
    current_user: UserResponse = Depends(get_current_user)
):
    """Get all users in a mood room"""
    room = db.query(MoodRoom).filter(MoodRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Mood room not found")
    
    # Logic to get room participants
    # This will depend on your data model for tracking participants
    
    return []  # Return list of participants

@router.post("/{room_id}/track")
async def update_room_track(
    room_id: UUID,
    track_data: dict,  # You might want to create a specific schema for track data
    db: db_dependency,
    current_user: UserResponse = Depends(get_current_user)
):
    """Update the current track playing in the room"""
    room = db.query(MoodRoom).filter(MoodRoom.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Mood room not found")
    
    room.current_track = track_data
    db.commit()
    
    return {"message": "Track updated successfully"}