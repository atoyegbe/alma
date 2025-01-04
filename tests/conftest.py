import asyncio
from typing import Annotated, Generator, TypedDict
import uuid

import httpx
import pytest

from fastapi import Depends, FastAPI
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
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
def app():
    use_route_names_as_operation_ids(test_app)
    yield test_app


@pytest.fixture(scope='session')
async def app_state(app):
    async with test_lifespan(app) as state:
        yield state



@pytest.fixture(scope="session", autouse=True)
def db_engine():
    """Create test database engine"""
    SQLModel.metadata.create_all(engine_test)
    yield
    SQLModel.metadata.drop_all(engine_test)


@pytest.fixture(autouse=True)
async def clean_db(db_test):
    yield
    for table in reversed(SQLModel.metadata.sorted_tables):
        db_test.execute(table.delete())
    db_test.commit()


@pytest.fixture(scope="function")
def db_test() -> Generator[Session, None, None]:
    """Create a fresh database session for each test"""
    with Session(engine_test) as session:
        yield session


db_dependency = Annotated[Session, Depends(db_test)]


class State(TypedDict):
    user_service: UserService
    auth_service: AuthService


@asynccontextmanager
async def test_lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient()
    app.state.user_service = UserService(db_dependency)
    app.state.auth_service = AuthService(db_dependency)
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
    user_service.create_user(user_data)


@pytest.fixture
async def client(app, sample_user: User):
    token = sample_user.spotify_token
    headers = {'Content-Type': 'application/json', 'Auth-Token': f'Bearer {token}'}

    async with httpx.AsyncClient(
        app=app, base_url='http://127.0.0.1:8000', headers=headers
    ) as client:
        print('Test Client is ready')
        yield client


@pytest.fixture
def test_user_profile(sample_user: User, user_service: UserService):
    music_profile = MusicProfile(
        id=uuid.uuid4(),
        user_id=sample_user.id,
        genres=["pop", "rock", "indie"],
        top_artists=["artist1", "artist2", "artist3"],
        top_tracks=["track1", "track2", "track3"],
        energy_score=0.8,
        danceability_score=0.7,
        diversity_score=0.6,
        obscurity_score=0.5,
    )
    db_test.add(music_profile)
    db_test.commit()
    db_test.refresh(music_profile)
    return music_profile


# @pytest.fixture
# def other_users(db_test: Session):
#     users = [
#         User(
#             id=uuid.uuid4(),
#             email=f"other{i}@example.com",
#             spotify_id=f"other_spotify_{i}",
#             display_name=f"Other User {i}",
#         )
#         for i in range(3)
#     ]
#     db_test.add_all(users)
#     db_test.commit()
#     db_test.refresh(users)
#     return users


# @pytest.fixture
# def other_profiles(other_users: List[User], db_test: Session):
#     other_profiles = [
#         MusicProfile(
#             id=uuid.uuid4(),
#             user_id=user.id,
#             genres=["rock", "indie", "electronic"],
#             top_artists=["artist2", "artist4", "artist5"],  # artist2 shared
#             top_tracks=["track2", "track4", "track5"],  # track2 shared
#             energy_score=0.75,
#             danceability_score=0.65,
#             diversity_score=0.55,
#             obscurity_score=0.45,
#         )
#         for user in other_users
#     ]
#     db_test.add_all(other_profiles)
#     db_test.commit()
#     db_test.refresh(other_profiles)
#     return other_profiles
