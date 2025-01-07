from contextlib import asynccontextmanager
from typing import AsyncIterator, TypedDict

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from starlette.middleware.sessions import SessionMiddleware

from app.connections.connections import ConnectionService
from app.auth.auth import AuthService
from app.users.users import UserService
from app.database.database import create_db_and_tables, engine

from app.connections.router import router as connections_router
from app.recommendation.router import router as recommendation_router
from app.auth.router import router as auth_router
from app.playlists.router import router as playlist_router
from app.users.router import router as user_router
from app.moodrooms.router import router as moodroom_router
from app.realtime.router import router as websocket_router


class State(TypedDict):
    user_service: UserService
    auth_service: AuthService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[State]:
    create_db_and_tables()
    app.state.http_client = httpx.AsyncClient()
    # Create a database session and pass it to services
    with Session(engine) as session:
        app.state.user_service = UserService(session)
        app.state.auth_service = AuthService(session)
        # app.state.connection_service = ConnectionService(
        #     session, app.state.user_service)
        yield {'user_service': app.state.user_service, 'auth_service': app.state.auth_service}

    await app.state.http_client.aclose()

app = FastAPI(lifespan=lifespan)

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
app.include_router(connections_router, prefix='/connections', tags=['Connections'])
app.include_router(
    recommendation_router, prefix='/recommendations', tags=['Recommendation']
)
app.include_router(playlist_router, prefix='/playlists', tags=['Playlists'])
app.include_router(user_router, prefix='/users', tags=['Users'])
app.include_router(moodroom_router, prefix='/mood-rooms', tags=['Mood Rooms'])
app.include_router(websocket_router, prefix='/ws', tags=['Realtime'])
