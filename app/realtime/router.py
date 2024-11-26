from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from uuid import UUID
from typing import Optional
from sqlmodel import Session

from app.auth.auth import get_current_user, get_user_by_token
from app.database.database import get_db as get_session
from app.realtime.handlers import manager
from app.realtime.models import (
    UserJoinedMessage,
    UserLeftMessage,
    ChatMessage,
    TrackUpdateMessage,
    WebSocketUser
)

router = APIRouter()

@router.websocket("/mood-rooms/{room_id}")
async def mood_room_websocket(
    websocket: WebSocket,
    room_id: UUID,
    token: Optional[str] = None
):
    """WebSocket endpoint for real-time mood room updates"""
    if not token:
        await websocket.close(code=4001, reason="Authentication required")
        return

    db = next(get_session())
    current_user = await get_user_by_token(db, token)
    if not current_user:
        await websocket.close(code=4001, reason="Invalid authentication token")
        return

    try:
        await manager.connect_to_room(websocket, room_id)
        
        # Create user info for messages
        user_info = WebSocketUser(
            id=str(current_user.id),
            name=current_user.display_name or current_user.username,
            avatar_url=current_user.avatar_url
        )
        
        # Notify others that user joined
        join_message = UserJoinedMessage(user=user_info)
        await manager.broadcast_to_room(room_id, join_message)

        try:
            while True:
                # Receive and validate messages
                data = await websocket.receive_json()
                message_type = data.get("type")
                
                if message_type == "message":
                    # Handle chat message
                    chat_message = ChatMessage(
                        user=user_info,
                        content=data.get("content", "")
                    )
                    await manager.broadcast_to_room(room_id, chat_message)
                
                elif message_type == "track_update":
                    # Handle track update
                    track_message = TrackUpdateMessage(
                        user=user_info,
                        track_id=data.get("track_id", ""),
                        track_name=data.get("track_name", ""),
                        artist_name=data.get("artist_name", "")
                    )
                    await manager.broadcast_to_room(room_id, track_message)

        except WebSocketDisconnect:
            await manager.disconnect_from_room(websocket, room_id)
            # Notify others that user left
            leave_message = UserLeftMessage(user=user_info)
            await manager.broadcast_to_room(room_id, leave_message)
    
    except Exception as e:
        await websocket.close(code=4000, reason=str(e))

@router.websocket("/notifications")
async def notifications_websocket(
    websocket: WebSocket,
    token: Optional[str] = None
):
    """WebSocket endpoint for real-time user notifications"""
    if not token:
        await websocket.close(code=4001, reason="Authentication required")
        return

    db = next(get_session())
    current_user = await get_user_by_token(db, token)
    if not current_user:
        await websocket.close(code=4001, reason="Invalid authentication token")
        return

    try:
        await manager.connect_to_notifications(websocket, current_user.id)
        try:
            while True:
                # Keep connection alive and handle incoming acknowledgments
                data = await websocket.receive_json()
        except WebSocketDisconnect:
            await manager.disconnect_from_notifications(current_user.id)
    
    except Exception as e:
        await websocket.close(code=4000, reason=str(e))
