from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
from uuid import UUID
from sqlmodel import SQLModel

from app.realtime.models import (
    BaseWebSocketMessage,
    UserJoinedMessage,
    UserLeftMessage,
    ChatMessage,
    TrackUpdateMessage,
    NotificationMessage,
    WebSocketUser,
)

# TODO: consider using Redis for real-time updates


class ConnectionManager:
    def __init__(self):
        # Store room connections: room_id -> set of websockets
        self.room_connections: Dict[UUID, Set[WebSocket]] = {}
        # Store user notification connections: user_id -> websocket
        self.notification_connections: Dict[UUID, WebSocket] = {}

    async def connect_to_room(self, websocket: WebSocket, room_id: UUID):
        await websocket.accept()
        if room_id not in self.room_connections:
            self.room_connections[room_id] = set()
        self.room_connections[room_id].add(websocket)

    async def disconnect_from_room(self, websocket: WebSocket, room_id: UUID):
        self.room_connections[room_id].remove(websocket)
        if not self.room_connections[room_id]:
            del self.room_connections[room_id]

    async def connect_to_notifications(self, websocket: WebSocket, user_id: UUID):
        await websocket.accept()
        self.notification_connections[user_id] = websocket

    async def disconnect_from_notifications(self, user_id: UUID):
        if user_id in self.notification_connections:
            del self.notification_connections[user_id]

    async def broadcast_to_room(self, room_id: UUID, message: BaseWebSocketMessage):
        """Send message to all users in a room"""
        if room_id in self.room_connections:
            disconnected_ws = set()
            message_dict = message.dict()
            for websocket in self.room_connections[room_id]:
                try:
                    await websocket.send_json(message_dict)
                except WebSocketDisconnect:
                    disconnected_ws.add(websocket)

            # Clean up disconnected websockets
            for ws in disconnected_ws:
                self.room_connections[room_id].remove(ws)

    async def send_notification(self, user_id: UUID, message: NotificationMessage):
        """Send notification to a specific user"""
        if user_id in self.notification_connections:
            try:
                await self.notification_connections[user_id].send_json(message.dict())
            except WebSocketDisconnect:
                await self.disconnect_from_notifications(user_id)


manager = ConnectionManager()
