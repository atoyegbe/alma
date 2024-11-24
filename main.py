import base64
import os
import urllib
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app.constant import API_BASE_URL, AUTH_URL, REDIRECT_URL, TOKEN_URL, CLIENT_ID, CLIENT_SECRET
from app.database import SessionLocal, engine
from app.models import Base
from app.schema import UserData, UserSchema
from app.users import (create_user, get_user, get_user_by_token, get_users,
                       update_user)

from app.auth.auth import requires_auth, get_header

from app.recommendation.router import router as recommendation_router
from app.auth.router import router as auth_router
from app.playlists.router import router as playlist_router
from app.users.router import router as user_router
from app.moodrooms import router as moodroom_router
from app.websockets.router import router as websocket_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient()
    yield
    await app.state.http_client.aclose()

app = FastAPI(lifespan=lifespan)
Base.metadata.create_all(bind=engine)

all_origins = ['*']

app.add_middleware(SessionMiddleware, secret_key="dhdhh37379fvckdetagsg")

app.add_middleware(
    CORSMiddleware,
    allow_origins=all_origins,
    allow_credentials=True,
    allow_methods=all_origins,
    allow_headers=all_origins,
)


app.include_router(auth_router, prefix='/auth', tags=['Auth'])
app.include_router(recommendation_router, prefix='/recommendation', tags=['Recommendation'])
app.include_router(playlist_router, prefix='/playlists', tags=['Playlists'])
app.include_router(user_router, prefix='/users', tags=['Users'])
app.include_router(moodroom_router, prefix='/mood-rooms', tags=['Mood Rooms'])
app.include_router(websocket_router, prefix='/ws', tags=['WebSocket'])