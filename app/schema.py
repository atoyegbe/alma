from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    country: Optional[str] = None
    auth_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_date: Optional[datetime] = None
    genres: List[str] = []
    top_tracks: List[str] = []
    top_artists: List[str] = []
    top_albums: List[str] = []


class UserData(BaseModel):
    username: str
    country: Optional[str] = None
    genres: List[str] = []
    top_tracks: List[str] = []
    top_artists: List[str] = []
    top_albums: List[str] = []

class UserSchema(UserBase):
    user_id: str
    created_at: Optional[str] = None

    class Config:
        from_attributes = True
