from typing import List, Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    country: Optional[str] = None
    geners: List[str] = []
    top_artists: List[str] = []
    top_albums: List[str] = []


class UserSchema(UserBase):
    user_id: str
    created_at: Optional[str] = None

    class Config:
        from_attributes = True