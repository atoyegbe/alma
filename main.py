import os
import urllib
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app.constant import API_BASE_URL, AUTH_URL, REDIRECT_URL, TOKEN_URL
from app.database import SessionLocal, engine
from app.models import Base, User
from app.schema import UserSchema
from app.users import (create_user, get_user, update_user)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient()
    app.state.db = SessionLocal()
    yield

app = FastAPI(lifespan=lifespan)
Base.metadata.create_all(bind=engine)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8000/callback",
]
app.add_middleware(SessionMiddleware, secret_key="dhdhh37379fvckdetagsg")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

client_id = os.getenv('SPOTIPY_CLIENT_ID', '')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET', '')


def get_header(request: Request):
    return {
        'Authorization': f"Bearer {request.session['access_token']}"
    }

async def requires_auth(request: Request) -> None:
    """
    Checks for a valid access token in the user's session and redirects
    to the login or refresh token route if necessary.
    """

    user_sessions = request.session

    if 'access_token' not in user_sessions:
        return RedirectResponse('/login')

    if datetime.now().timestamp() > user_sessions['expires_at']:
        return RedirectResponse('/refresh_token')

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
            request.session['access_token'] = token_info['access_token']
            request.session['refresh_token'] = token_info['refresh_token']
            request.session['expires_at'] = datetime.now().timestamp() +  token_info['expires_in']

            return RedirectResponse('/user')
        except httpx.RequestError as e:
            # Handle request errors (e.g., connection error)
            raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")


@app.get('/refresh-token')
async def refresh_token(request: Request):
    if 'refresh_token' not in request.session:
        return RedirectResponse('/login')

    if datetime.now().timestamp() > request.session['expires_at']:
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': request.session['refresh_token'],
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
            request.session['access_token'] = new_token_info['access_token']
            request.session['expires_at'] = datetime.now().timestamp() +  new_token_info['expires_in']

            return RedirectResponse('/playlists')
        except httpx.RequestError as e:
            # Handle request errors (e.g., connection error)
            raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")


@app.get('/user', dependencies=[Depends(requires_auth)])
async def get_user_data(request: Request, db: db_dependency):
    try:
        user_id = request.session.get('user_id')
        existing_user: User = None
        if user_id:
            existing_user = await get_user(db, request.session.get('user_id'))
    
        if not existing_user:
            response = await app.state.http_client.get(f"{API_BASE_URL}me", headers=get_header(request))
            user_data = response.json()

            request.session['user_id'] = user_data['id']
            new_user = UserSchema(user_id=user_data['id'], username=user_data['display_name'], country=user_data['country'])
            await create_user(db, new_user)

            await save_user_top_tracks(request)
            await save_top_artists(request)

            return {'message': 'user details saved'}
        return existing_user

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")


@app.get('/playlists', dependencies=[Depends(requires_auth)])
async def get_playlists(request: Request):
    try:
        response = await app.state.http_client.get(f"{API_BASE_URL}me/playlists", 
                                                    headers=get_header(request))
        playlists = response.json()
        return playlists
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")


async def get_followed_artist(request: Request):
    try:
        response = await app.state.http_client.get(f"{API_BASE_URL}me/following?type=artist",
                                                   headers=get_header(request))
        artists = response.json()
        return artists
    except httpx.RequestError as e:
        raise HTTPException(status_code=400, detail=f"Request error: {str(e)}")

async def save_top_artists(request: Request):
    response = await app.state.http_client.get(f"{API_BASE_URL}me/top/artists?time_range=long_term",
                                               headers=get_header(request))
    resp = response.json()
    top_artists = [track['name'] for track in resp['items']]
    genres_list = [track['genres'] for track in resp['items']]
    flattened_list = [genre for genres in genres_list for genre in genres]

    print('saving user genres and top artists' )
    await update_user(app.state.db, request.session['user_id'],
                       **{'top_artists': top_artists, 'genres': list(set(flattened_list))})
    

async def save_user_top_tracks(request: Request):
    response = await app.state.http_client.get(f"{API_BASE_URL}me/top/tracks?time_range=long_term",
                                               headers=get_header(request))
    resp = response.json()
    top_tracks = [track['name'] for track in resp['items']]
    print('saving user top tracks')
    await update_user(app.state.db, request.session['user_id'], **{'top_tracks': top_tracks})
