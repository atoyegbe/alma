from typing import List
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from sqlmodel import Session, select

from app.auth.auth import get_current_user
from app.database.database import db_dependency
from app.models.models import MoodRoom, User

router = APIRouter()


@router.get("/", response_model=List[MoodRoom])
async def list_mood_rooms(
    db: db_dependency, current_user: User = Depends(get_current_user)
):
    """List all available mood rooms"""
    statement = select(MoodRoom)
    rooms = db.exec(statement).all()
    return rooms


@router.get("/{room_id}", response_model=MoodRoom)
async def get_room_details(
    room_id: UUID, db: db_dependency, current_user: User = Depends(get_current_user)
):
    """Get details of a specific mood room"""
    statement = select(MoodRoom).where(MoodRoom.id == room_id)
    room = db.exec(statement).first()
    if not room:
        raise HTTPException(status_code=404, detail="Mood room not found")
    return room


@router.post("/join/{room_id}")
async def join_room(
    room_id: UUID, db: db_dependency, current_user: User = Depends(get_current_user)
):
    """Join a mood room"""
    # Check if room exists
    room_statement = select(MoodRoom).where(MoodRoom.id == room_id)
    room = db.exec(room_statement).first()
    if not room:
        raise HTTPException(status_code=404, detail="Mood room not found")

    # TODO Logic to add user to room participants
    # This will depend on how you're tracking room participants
    # You might want to create a room_participants table

    return {"message": "Successfully joined the room"}


@router.post("/leave/{room_id}")
async def leave_room(
    room_id: UUID, db: db_dependency, current_user: User = Depends(get_current_user)
):
    """Leave a mood room"""
    # Check if room exists
    room_statement = select(MoodRoom).where(MoodRoom.id == room_id)
    room = db.exec(room_statement).first()
    if not room:
        raise HTTPException(status_code=404, detail="Mood room not found")

    # TODO Logic to remove user from room participants

    return {"message": "Successfully left the room"}


@router.get("/{room_id}/users", response_model=List[User])
async def get_room_users(
    room_id: UUID, db: db_dependency, current_user: User = Depends(get_current_user)
):
    """Get all users in a mood room"""
    # Check if room exists
    room_statement = select(MoodRoom).where(MoodRoom.id == room_id)
    room = db.exec(room_statement).first()
    if not room:
        raise HTTPException(status_code=404, detail="Mood room not found")

    # TODO Logic to get room participants
    # This will depend on your data model for tracking participants

    return []  # Return list of participants


# @router.post("/{room_id}/track")
# async def update_room_track(
#     room_id: UUID,
#     track_data: TrackUpdate,
#     db: db_dependency,
#     current_user: User = Depends(get_current_user)
# ):
#     """Update the current track playing in the room"""
#     # Check if room exists and user is a participant
#     room_statement = select(MoodRoom).where(MoodRoom.id == room_id)
#     room = db.exec(room_statement).first()
#     if not room:
#         raise HTTPException(status_code=404, detail="Mood room not found")

#     db.commit()
#     db.refresh(room)

#     return {"message": "Track updated successfully"}
