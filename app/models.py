from datetime import datetime
from typing import List, Optional


from pydantic import BaseModel


class User(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None
    name: Optional[str] = None
    created_at: Optional[datetime] = None
    friends:  List[str] = []
    country: Optional[str] = None
    soulmates: List[str] = []
    genres: Optional[str] = None
    top_artists = List[str] =  []
    top_albums = List[str] = []
