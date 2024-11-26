import asyncio
import os
from typing import Generator
from datetime import datetime
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.database import Base, get_db
from app.main import app

# Database URLs
POSTGRES_TEST_URL = "postgresql://postgres:test@localhost:5432/alma_test"
SQLITE_TEST_URL = "sqlite:///./test.db"

def get_database_url(request) -> str:
    """
    Determine which database to use based on test markers.
    Use PostgreSQL for integration tests and SQLite for unit tests.
    """
    markers = [marker.name for marker in request.node.iter_markers()]
    return POSTGRES_TEST_URL if "integration" in markers else SQLITE_TEST_URL

@pytest.fixture(scope="session")
def engine_integration():
    """Create a PostgreSQL test database engine for integration tests."""
    engine = create_engine(
        POSTGRES_TEST_URL,
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

@pytest.fixture(scope="session")
def engine_unit():
    """Create a SQLite test database engine for unit tests."""
    engine = create_engine(
        SQLITE_TEST_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Enable foreign key support for SQLite
    def _fk_pragma_on_connect(dbapi_con, con_record):
        dbapi_con.execute('pragma foreign_keys=ON')
    
    event.listen(engine, 'connect', _fk_pragma_on_connect)
    
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("./test.db"):
        os.remove("./test.db")

@pytest.fixture(scope="function")
def engine(request, engine_integration, engine_unit):
    """Provide the appropriate engine based on test type."""
    markers = [marker.name for marker in request.node.iter_markers()]
    return engine_integration if "integration" in markers else engine_unit

@pytest.fixture(scope="function")
def db_session(engine):
    """Create a fresh database session for each test."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with a fresh database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def async_client(client):
    """Create an async test client."""
    return client

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def sample_user(db_session):
    """Create a sample user for testing."""
    from app.models.datamodels import User
    user = User(
        id=str(uuid.uuid4()),
        username="test_user",
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
        created_at=datetime.utcnow()
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user