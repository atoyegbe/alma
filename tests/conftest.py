import asyncio
from typing import AsyncIterator, Dict, TypedDict

import httpx
import pytest

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.routing import APIRoute
from sqlmodel import Session, SQLModel, create_engine

from app.auth.auth import AuthService
from app.users.users import UserService
from app.models.models import MusicProfile, User
from app.main import app as test_app

# Use test database
TEST_DATABASE_URL = "postgresql://postgres:test@localhost:5432/alma_test"

# Create test engine
engine_test = create_engine(
    TEST_DATABASE_URL, echo=False  # Set to False to reduce test output noise
)

def use_route_names_as_operation_ids(app: FastAPI) -> None:
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    asyncio.set_event_loop(loop)
    print("Event Loop Initialized")
    yield loop
    print("Event Loop Closed")
    loop.close()


@pytest.fixture(scope='session')
def app():
    use_route_names_as_operation_ids(test_app)
    yield test_app


class State(TypedDict):
    user_service: UserService
    auth_service: AuthService


@pytest.fixture(scope="session")
def db_test():
    """Create a fresh database session for each test"""
    with Session(engine_test) as session:
        print(f"Initializing DB Session: {id(session)}")
        yield session
        print(f"Closing DB Session: {id(session)}")


@pytest.fixture(scope="session", autouse=True)
async def app_state(app, db_test):
    async with test_lifespan(app, db_test) as state:
        yield state


@pytest.fixture(scope="session", autouse=True)
def db_engine():
    """Create test database engine"""
    SQLModel.metadata.create_all(engine_test)
    yield
    # SQLModel.metadata.drop_all(engine_test)



@asynccontextmanager
async def test_lifespan(app: FastAPI, db_test: Session) -> AsyncIterator[State]:
    app.state.user_service = UserService(db_test)
    app.state.auth_service = AuthService(db_test)
    app.state.http_client = httpx.AsyncClient()

    yield {'user_service': app.state.user_service, 'auth_service': app.state.auth_service}

    await app.state.http_client.aclose()


@pytest.fixture(scope='session')
async def user_service(app_state):
    user_service = app_state['user_service']
    yield user_service


@pytest.fixture(scope='session')
async def auth_service(app_state):
    auth_service = app_state['auth_service']
    yield auth_service


@pytest.fixture
async def sample_user(user_service: UserService):
    """Create a sample user for testing."""
    user_data = {
        'display_name': 'sample_test_user',
        'email': 'test_sample@example.com',
        'spotify_token': 'spotify_token',
        'spotify_id': 'test_spotify_id',
    }
    new_user = user_service.create_user(user_data)

    new_music_profile: Dict = {
        'genres': ['rock', 'indie', 'electronic'],
        'top_artists': ['drake', 'olamide', 'wizkid', 'saint jhn'],
        'top_tracks': ['mood', 'louder', 'one dance'],
        'energy_score': 0.75,
        'danceability_score': 0.65,
        'diversity_score': 0.55,
        'obscurity_score': 0.45,
    }
    user_service.update_user_music_profile(
        new_user.id, new_music_profile)

    return new_user


@pytest.fixture
async def other_sample_user(user_service: UserService):
    """Create a sample user for testing."""
    user_data = {
        'display_name': 'other_sample_test_user',
        'email': 'other_test_sample@example.com',
        'spotify_token': 'other_spotify_token',
        'spotify_id': 'other_test_spotify_id',
    }
    new_user = user_service.create_user(user_data)

    new_music_profile: Dict = {
        'genres': ['afro pop', 'hiphop', 'rnb'],
        'top_artists': ['asake', 'olamide', 'wizkid'],
        'top_tracks': ['mood', 'new religion', 'ye'],
        'energy_score': 0.65,
        'danceability_score': 0.75,
        'diversity_score': 0.50,
        'obscurity_score': 0.65,
    }
    user_service.update_user_music_profile(
        new_user.id, new_music_profile)

    return new_user


@pytest.fixture
async def get_other_sample_user_profile(
        other_sample_user: User,
        user_service: UserService
        ) -> MusicProfile:
    other_sample_user_profile = user_service.get_music_profile(
        other_sample_user.id)
    return other_sample_user_profile


@pytest.fixture
async def client(app, sample_user: User):
    token = sample_user.spotify_token
    headers = {'Content-Type': 'application/json', 'auth-token': f'Bearer {token}'}

    async with httpx.AsyncClient(
        app=app, base_url='http://127.0.0.1:8000', headers=headers
    ) as client:
        print('Test Client is ready')
        yield client



## TODO: Alternative

# @pytest.fixture
# def client():
#     # Set up the TestClient with the FastAPI app
#     client = TestClient(test_app)
#     yield client


# @pytest.fixture
# def get_header(sample_user: User) -> Dict:
#     token = sample_user.spotify_token
#     return {'Content-Type': 'application/json', 'auth-token': f'Bearer {token}'}
