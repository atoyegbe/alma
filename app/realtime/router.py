from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from uuid import UUID

from app.auth.auth import get_authenticated_user
from app.models.models import User
from app.users.users import UserService
from app.helpers.router.utils import get_user_service
from app.realtime.handlers import manager
from app.realtime.models import (
    UserJoinedMessage,
    UserLeftMessage,
    ChatMessage,
    TrackUpdateMessage,
    WebSocketUser,
)

router = APIRouter()


@router.websocket("/mood-rooms/{room_id}")
async def mood_room_websocket(
    websocket: WebSocket,
    room_id: UUID,
    current_user: User = Depends(get_authenticated_user),
    user_service: UserService = Depends(get_user_service),
):
    """WebSocket endpoint for real-time mood room updates"""
    current_user: User = await user_service.get_user(current_user.id)
    if not current_user:
        await websocket.close(code=4001, reason="Invalid authentication token")
        return

    try:
        await manager.connect_to_room(websocket, room_id)

        # Create user info for messages
        user_info = WebSocketUser(
            id=str(current_user.id),
            name=current_user.display_name,
            avatar_url=current_user.spotify_image_url,
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
                        user=user_info, content=data.get("content", "")
                    )
                    await manager.broadcast_to_room(room_id, chat_message)

                elif message_type == "track_update":
                    # Handle track update
                    track_message = TrackUpdateMessage(
                        user=user_info,
                        track_id=data.get("track_id", ""),
                        track_name=data.get("track_name", ""),
                        artist_name=data.get("artist_name", ""),
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
    current_user: User = Depends(get_authenticated_user),
    user_service: UserService = Depends(get_user_service),
):
    """WebSocket endpoint for real-time user notifications"""
    current_user: User = await user_service.get_user(current_user.id)
    if not current_user:
        await websocket.close(code=4001, reason="Invalid authentication token")
        return

    try:
        await manager.connect_to_notifications(websocket, current_user.id)
        try:
            while True:
                # Keep connection alive and handle incoming acknowledgments
                await websocket.receive_json()
        except WebSocketDisconnect:
            await manager.disconnect_from_notifications(current_user.id)

    except Exception as e:
        await websocket.close(code=4000, reason=str(e))
