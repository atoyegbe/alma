import os

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token?'
API_BASE_URL = 'https://api.spotify.com/v1/'
REDIRECT_URL = 'http://127.0.0.1:8000/callback'
CLIENT_REDIRECT_URL = 'http://localhost:3000/login'

CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET", "")