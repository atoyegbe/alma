from datetime import datetime
from typing import Optional, Dict, Any, Literal
from uuid import UUID
from sqlmodel import SQLModel

class WebSocketUser(SQLModel):
    """User information in websocket messages"""
    id: str
    name: str
    avatar_url: Optional[str] = None

class BaseWebSocketMessage(SQLModel):
    """Base model for all websocket messages"""
    type: str
    timestamp: datetime = datetime.utcnow()

class UserJoinedMessage(BaseWebSocketMessage):
    """Message sent when a user joins a room"""
    type: Literal["user_joined"] = "user_joined"
    user: WebSocketUser

class UserLeftMessage(BaseWebSocketMessage):
    """Message sent when a user leaves a room"""
    type: Literal["user_left"] = "user_left"
    user: WebSocketUser

class ChatMessage(BaseWebSocketMessage):
    """Message sent for room chat"""
    type: Literal["message"] = "message"
    user: WebSocketUser
    content: str

class TrackUpdateMessage(BaseWebSocketMessage):
    """Message sent when track is updated"""
    type: Literal["track_update"] = "track_update"
    track_id: str
    track_name: str
    artist_name: str
    user: WebSocketUser

class NotificationMessage(BaseWebSocketMessage):
    """Message sent for user notifications"""
    type: Literal["notification"] = "notification"
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
