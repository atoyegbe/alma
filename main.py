import os
import urllib
from datetime import datetime

import httpx
from app.constant import API_BASE_URL, AUTH_URL, REDIRECT_URL, TOKEN_URL
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from redis import Redis

from app.users import get_user_info, save_user_info

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = Redis(host='localhost', port=6379)
    app.state.http_client = httpx.AsyncClient()
    yield
    app.state.redis.closee()

app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


client_id = os.getenv('SPOTIPY_CLIENT_ID', '')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET', '')

# In-memory database to store user sessions
# TODO: implement a proper session manager (using redis)
user_sessions = {}


def get_header():
    return {
        'Authorization': f"Bearer {user_sessions['access_token']}"
    }


@app.get('/', response_class=HTMLResponse)
async def index():
    return "Welcome to my Spotify App <a href='/login'> Login with Spotify.</a>"


@app.get('/login')
async def auth_user():

    query_params = {
      'client_id': client_id,
      'scope': 'user-top-read user-follow-read user-library-read user-read-private',
      'response_type': 'code',
      'redirect_uri': REDIRECT_URL,
      'show_dialog': True,
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

        try:
            response = await app.state.http_client.post(TOKEN_URL, data=req_body)

            # Check if the response indicates an error (status code 4xx or 5xx)
            if response.status_code >= 400:
                raise HTTPException(status_code=response.status_code, detail=f"Callback error: {response.text}")

            token_info = response.json()
            user_sessions['access_token'] = token_info['access_token']
            user_sessions['refresh_token'] = token_info['refresh_token']
            user_sessions['expires_at'] = datetime.now().timestamp() +  token_info['expires_in']

            return RedirectResponse('/user')
        except httpx.RequestError as e:
            # Handle request errors (e.g., connection error)
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

        try:
            # Make a request to the callback URL
            response = await app.state.http_client.post(TOKEN_URL, data=req_body)

            # Check if the response indicates an error (status code 4xx or 5xx)
            if response.status_code >= 400:
                raise HTTPException(
                    status_code=response.status_code, 
                    detail=f"Callback error: {response.text}")

            new_token_info = response.json()
            user_sessions['access_token'] = new_token_info['access_token']
            user_sessions['expires_at'] = datetime.now().timestamp() +  new_token_info['expires_in']

            return RedirectResponse('/playlists')
        except httpx.RequestError as e:
            # Handle request errors (e.g., connection error)
            raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")


@app.get('/user')
async def get_user_data():
    if 'access_token' not in user_sessions:
        return RedirectResponse('/login')

    if datetime.now().timestamp() > user_sessions['expires_at']:
        return RedirectResponse('/refresh_token')

    try:
        response = await app.state.http_client.get(f"{API_BASE_URL}me", headers=get_header())
        user_data = response.json()
        # move checking if the user exist outside this block, check if a user exist in the db before make this request
        # if a user does exist in the db no need to make a request to get user data.
        user = await get_user_info(user_data['id'])
        if not user:
            await save_user_info(user_data)
            return {'message': 'user details saved'}
        return user
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")


@app.get('/playlists')
async def get_playlists(request: Request):
    if 'access_token' not in app.state.redis:
        return RedirectResponse('/login')

    if datetime.now().timestamp() > user_sessions['expires_at']:
        return RedirectResponse('/refresh_token')

    user_id = request.query_params('user_id')

    if user_id:
        try:
            response = await app.state.http_client.get(f"{API_BASE_URL}{user_id}/playlists", headers=get_header())
            playlists = response.json()
            return playlists
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")
