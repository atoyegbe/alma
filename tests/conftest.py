from typing import Generator
import os
import asyncio
from datetime import datetime
import uuid
import sys


import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.database.database import get_db
from app.main import app

# Use test database
TEST_DATABASE_URL = "postgresql://postgres:test@localhost:5432/alma_test"

# Create test engine
engine_test = create_engine(
    TEST_DATABASE_URL,
    echo=True  # Set to False to reduce test output noise
)

@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine"""
    SQLModel.metadata.create_all(engine_test)
    yield engine_test
    SQLModel.metadata.drop_all(engine_test)

@pytest.fixture(scope="function")
def db(db_engine) -> Generator[Session, None, None]:
    """Create a fresh database session for each test"""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db) -> Generator[TestClient, None, None]:
    """Create a test client with database session override"""
    def get_test_db():
        yield db

    app.dependency_overrides[get_db] = get_test_db
    with TestClient(main_app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def setup_db(db: Session):
    """Automatically set up and tear down database for each test"""
    SQLModel.metadata.create_all(engine_test)
    yield
    db.rollback()

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def sample_user(db):
    """Create a sample user for testing."""
    from app.models.models import User
    user = User(
        id=str(uuid.uuid4()),
        username="test_user",
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
        created_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user