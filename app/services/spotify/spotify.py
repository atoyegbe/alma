import os
from interface import StreamData

CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID', '')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET', '')

class SpotifyService(StreamData):
    def __init__(self):
        pass

    async def get_user_playlist(self):
        pass

    async def get_top_artists(self):
        pass
    
    async def get_top_tracks(self):
        pass
    
    async def get_followed_artists(self):
        pass

