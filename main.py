import os
import urllib
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated, List, Optional

import httpx
from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app.constant import API_BASE_URL, AUTH_URL, REDIRECT_URL, TOKEN_URL
from app.database import SessionLocal, engine
from app.models import Base
from app.schema import UserSchema
from app.similarity import get_users_similiraity
from app.users import (create_user, get_user, get_user_by_token, get_users,
                       update_user)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient()
    yield
    await app.state.http_client.aclose()

app = FastAPI(lifespan=lifespan)
Base.metadata.create_all(bind=engine)

origins = [
    "*",
    "http://localhost:8000",
    "http://localhost:3000/",
    "http://localhost:3000/callback",
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


def get_header(token: str):
    return {
        'Authorization': f"Bearer {token}"
    }

async def requires_auth(request: Request, auth_token: Optional[str] = Header(None)) -> UserSchema:
    """
    Validate user
    """
    if not auth_token:
        raise HTTPException(status_code=401, detail='No auth header')

    if not auth_token.startswith('Bearer'):
        raise HTTPException(
            status_code=401, detail="'Bearer' prefix missing"
        )

    token = auth_token[7:]
    if not token:
        raise HTTPException(
            status_code=401, detail='No token in auth header'
        )

    db = get_db()
    current_user = get_user_by_token(db, auth_token)
    if not current_user:
       raise HTTPException(
            status_code=401, detail='Unable to authenticate user'
        )
    return current_user


@app.get('/login')
async def auth_user():
    query_params = {
      'client_id': client_id,
      'scope': 'user-top-read user-follow-read user-library-read user-read-private user-read-email',
      'response_type': 'code',
      'redirect_uri': REDIRECT_URL,
      'show_dialog': True,
    }
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(query_params)}"

    return RedirectResponse(auth_url, status_code=status.HTTP_302_FOUND)


@app.get('/callback')
async def callback(request: Request, db: Session = Depends(get_db), background_tasks: BackgroundTasks = Depends()):
    error_param = request.query_params.get("error")
    code_param = request.query_params.get("code")

    if error_param:
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

            if response.status_code >= 400:
                raise HTTPException(status_code=response.status_code, detail=f"Callback error: {response.text}")
            token_info = response.json()
            
            user_response = await app.state.http_client.get(f"{API_BASE_URL}me", headers={ 'Authorization': f"Bearer {token_info['access_token']}"})
            user_data = user_response.json()
            new_user = UserSchema(
                user_id=user_data['id'],
                username=user_data['display_name'],
                country=user_data['country'],
                auth_token=token_info['access_token'],
                refresh_token=token_info['refresh_token'],
                token_expires_date=datetime.now().timestamp() +  token_info['expires_in']
            )
            await create_user(db, new_user)

            background_tasks.add_task(save_user_top_tracks, new_user.auth_token, db)
            background_tasks.add_task(save_top_artists, new_user.auth_token, db)
            # todo: run this in backgorund task in RedirectResponse
            await save_user_top_tracks(new_user.auth_token, db)
            await save_top_artists(new_user.auth_token, db)
            return RedirectResponse('http://localhost:3000/dashboard', background=)
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")


@app.get('/refresh-token')
async def refresh_token(refresh_token: str, request: Request):
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


@app.get('/profile', response_model=UserSchema)
async def get_user_data(
    db: Session = Depends(get_db),
    current_user = Annotated[UserSchema,Depends(requires_auth)]
):
    try:
        user = await get_user(db, current_user.user_id)
        return UserSchema(*user)
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")


@app.get(
        '/users', 
        response_model=List[UserSchema],
        dependencies=[Depends(requires_auth)]
)
async def get_all_users(db: Session = Depends(get_db)):
    # todo : ability to filter users by genres
    try:
        return await get_users(db)
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")


class SimilarityPercentage(BaseModel):
    similarity_score: int

@app.get('/check-match', response_model=SimilarityPercentage)
async def check_match(
    request: Request, 
    db: Session = Depends(get_db),
    current_user = Annotated[UserSchema, Depends(requires_auth)]
):
    match_id = request.query_params['match_id']
    match_user = await get_user(db, match_id)
    if not match_user:
        return {'message': 'users does not exist'}

    similarity_score = get_users_similiraity(current_user, match_user)
    
    # converting cosine similarity score to percentage
    similarity_score = 0.0 if similarity_score == 0.0 else (similarity_score + 1) / 2 * 100

    return SimilarityPercentage(similarity_score)


@app.get('/playlists', dependencies=[Depends(requires_auth)])
async def get_playlists(token: str):
    try:
        response = await app.state.http_client.get(f"{API_BASE_URL}me/playlists", 
                                                    headers=get_header(token))
        playlists = response.json()
        return playlists
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")


async def get_followed_artist(token: str):
    try:
        response = await app.state.http_client.get(f"{API_BASE_URL}me/following?type=artist",
                                                   headers=get_header(token))
        artists = response.json()
        return artists
    except httpx.RequestError as e:
        raise HTTPException(status_code=400, detail=f"Request error: {str(e)}")

async def save_top_artists(token: str,  db: Session = Depends(get_db)):
    response = await app.state.http_client.get(f"{API_BASE_URL}me/top/artists?time_range=long_term",
                                               headers=get_header(token))
    resp = response.json()
    top_artists = [track['name'] for track in resp['items']]
    genres_list = [track['genres'] for track in resp['items'] if track['genres']]
    flattened_list = [genre for genres in genres_list for genre in genres]

    print('saving user genres and top artists' )
    current_user = await get_user_by_token(db, token)
    await update_user(db, current_user.user_id,
                       **{'top_artists': top_artists, 'genres': list(set(flattened_list))})
    

async def save_user_top_tracks(token: str, db: Session = Depends(get_db)):
    response = await app.state.http_client.get(f"{API_BASE_URL}me/top/tracks?time_range=long_term",
                                               headers=get_header(token))
    resp = response.json()
    print('res', resp)
    top_tracks = [track['name'] for track in resp['items']]
    current_user = await get_user_by_token(db, token)
    await update_user(db, current_user.user_id, **{'top_tracks': top_tracks})


# todo: use a post request. 
@app.get('/follow', dependencies=[Depends(requires_auth)])
async def follow_user(request: Request, db: Session = Depends(get_db)):
    try:
        # json_data = request.json()
        # friend_id = json_data['friend_id']
        friend_id= request.query_params['friend_id']
        user_id = request.session.get('user_id')

        friend = await get_user(db, friend_id)
        await update_user(db, user_id, **{'friends': [friend]})
        print(f'{user_id} followed {friend_id}')
        return {'message': 'success'}

    except:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")

