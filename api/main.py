from datetime import datetime
import os
import urllib

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx

from .constant import AUTH_URL, API_BASE_URL, REDIRECT_URL, TOKEN_URL


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8000/callback",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


client_id = os.getenv('SPOTIPY_CLIENT_ID', '')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET', '')


# # In-memory database to store user sessions
user_sessions = {}


@app.get('/', response_class=HTMLResponse)
async def index():
    return "Welcome to my Spotify App <a href='/login'> Login with Spotify.</a>"


@app.get('/login')
async def auth_user():

    query_params = {
      'client_id': client_id,
      'scope': 'user-top-read user-follow-read user-library-read user-read-private',
      'response_type': 'code',
      'show_dialog': REDIRECT_URL,
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(query_params)}"

    return RedirectResponse(auth_url, status_code=status.HTTP_302_FOUND)


@app.get('/callback')
async def callback(request: Request):
    error_param = request.query_params.get("error")
    code_param = request.query_params.get("code")

    if error_param:
        # Handle the case where "error" parameter exists
        raise HTTPException(status_code=400, detail=f"Error in callback: {error_param}")

    if code_param:
        req_body = {
            'code': code_param,
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URL,
            'client_id': client_id,
            'client_secret': client_secret,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(TOKEN_URL, data=req_body)

                # Check if the response indicates an error (status code 4xx or 5xx)
                if response.status_code >= 400:
                    raise HTTPException(status_code=response.status_code, detail=f"Callback error: {response.text}")

                token_info = response.json()
                user_sessions['access_token'] = token_info['access_token']
                user_sessions['refresh_token'] = token_info['refresh_token']
                user_sessions['expires_at'] = datetime.now().timestamp() +  token_info['expires_in']

                return RedirectResponse('/users')
            except httpx.RequestError as e:
                # Handle request errors (e.g., connection error)
                raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")


@app.get('/users')
async def get_user_data():
    if 'access_token' not in user_sessions:
        return RedirectResponse('/login')

    if datetime.now().timestamp() > user_sessions['expires_at']:
        return RedirectResponse('/refresh_token')

    headers = {
        'Authorization': f"Bearer {user_sessions['access_token']}"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}me", headers=headers)
            playlists = response.json()
            return playlists
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")


@app.get('/playlists')
async def get_playlists(request: Request):
    if 'access_token' not in user_sessions:
        return RedirectResponse('/login')

    if datetime.now().timestamp() > user_sessions['expires_at']:
        return RedirectResponse('/refresh_token')

    headers = {
        'Authorization': f"Bearer {user_sessions['access_token']}"
    }

    user_id = request.query_params('user_id')

    if user_id:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{API_BASE_URL}{user_id}/playlists", headers=headers)
                playlists = response.json()
                return playlists
            except httpx.RequestError as e:
                raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")


@app.get('/refresh-token')
async def refresh_token():
    if 'refresh_token' not in user_sessions:
        return RedirectResponse('/login')
    
    if datetime.now().timestamp() > user_sessions['expires_at']:
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': user_sessions['refresh_token'],
            'client_id': client_id,
            'client_secret': client_secret
        }

        async with httpx.AsyncClient() as client:
            try:
                # Make a request to the callback URL
                response = await client.post(TOKEN_URL, data=req_body)

                # Check if the response indicates an error (status code 4xx or 5xx)
                if response.status_code >= 400:
                    raise HTTPException(status_code=response.status_code, detail=f"Callback error: {response.text}")

                new_token_info = response.json()
                user_sessions['access_token'] = new_token_info['access_token']
                user_sessions['expires_at'] = datetime.now().timestamp() +  new_token_info['expires_in']

                return RedirectResponse('/playlists')
            except httpx.RequestError as e:
                # Handle request errors (e.g., connection error)
                raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")


@app.get('/friends')
async def get_friends():
    return {'firends': ['list of friends']}


@app.get('/vote_song')
async def song_poll():
    return {'vote': 'vote your favorite songs'}


