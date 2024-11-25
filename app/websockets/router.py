from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from uuid import UUID
from typing import Optional

from app.auth.auth import get_current_user, get_user_by_token
from app.database.database import get_db
from app.websockets.handlers import manager
from app.models.schema import UserResponse

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

    db = next(get_db())
    current_user = await get_user_by_token(db, token)
    if not current_user:
        await websocket.close(code=4001, reason="Invalid authentication token")
        return

    try:
        await manager.connect_to_room(websocket, room_id)
        
        # Notify others that user joined
        await manager.broadcast_to_room(
            room_id,
            {
                "type": "user_joined",
                "user": {
                    "id": str(current_user.id),
                    "name": current_user.name
                }
            }
        )

        try:
            while True:
                # Receive and broadcast messages
                data = await websocket.receive_json()
                await manager.broadcast_to_room(
                    room_id,
                    {
                        "type": "message",
                        "user": {
                            "id": str(current_user.id),
                            "name": current_user.name
                        },
                        "content": data
                    }
                )
        except WebSocketDisconnect:
            # Notify others that user left
            await manager.broadcast_to_room(
                room_id,
                {
                    "type": "user_left",
                    "user": {
                        "id": str(current_user.id),
                        "name": current_user.name
                    }
                }
            )
        finally:
            await manager.disconnect_from_room(websocket, room_id)
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

    db = next(get_db())
    current_user = await get_user_by_token(db, token)
    if not current_user:
        await websocket.close(code=4001, reason="Invalid authentication token")
        return

    try:
        await manager.connect_to_notifications(websocket, current_user.id)
        try:
            # Keep connection alive and handle incoming acknowledgments
            while True:
                data = await websocket.receive_json()
                # Handle any acknowledgment logic here if needed
        except WebSocketDisconnect:
            pass
        finally:
            await manager.disconnect_from_notifications(current_user.id)
    except Exception as e:
        await websocket.close(code=4000, reason=str(e))
