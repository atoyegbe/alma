import pytest
from uuid import UUID, uuid4
from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.models import User, Connection, MusicProfile
from app.connections.connections import (
    get_user_connections,
    create_connection,
    accept_connection,
    reject_connection,
    delete_connection
)

@pytest.fixture
def test_user():
    return User(
        id=uuid4(),
        email="test@example.com",
        name="Test User",
        spotify_id="test_spotify_id"
    )

@pytest.fixture
def test_target_user():
    return User(
        id=uuid4(),
        email="target@example.com",
        name="Target User",
        spotify_id="target_spotify_id"
    )

@pytest.fixture
def test_music_profile(test_user):
    return MusicProfile(
        user_id=test_user.id,
        genres=["pop", "rock"],
        top_artists=[
            {"id": "artist1", "name": "Artist 1"},
            {"id": "artist2", "name": "Artist 2"}
        ]
    )

@pytest.fixture
def test_target_music_profile(test_target_user):
    return MusicProfile(
        user_id=test_target_user.id,
        genres=["rock", "jazz"],
        top_artists=[
            {"id": "artist2", "name": "Artist 2"},
            {"id": "artist3", "name": "Artist 3"}
        ]
    )

@pytest.fixture
def test_connection(test_user, test_target_user):
    return Connection(
        id=uuid4(),
        user_id=test_user.id,
        connected_user_id=test_target_user.id,
        status="pending",
        compatibility_score=0.75,
        shared_genres=["rock"],
        shared_artists=["artist2"]
    )

class TestConnections:
    def test_get_user_connections(self, db: Session, test_user, test_connection):
        # Setup
        db.add(test_connection)
        db.commit()

        # Execute
        connections = get_user_connections(db, test_user.id)

        # Assert
        assert len(connections) == 1
        assert connections[0].user_id == test_user.id
        assert connections[0].connected_user_id == test_connection.connected_user_id

    def test_create_connection(self, db: Session, test_user, test_target_user, 
                             test_music_profile, test_target_music_profile):
        # Setup
        db.add(test_music_profile)
        db.add(test_target_music_profile)
        db.commit()

        # Execute
        connection = create_connection(db, test_user.id, test_target_user.id)

        # Assert
        assert connection.user_id == test_user.id
        assert connection.connected_user_id == test_target_user.id
        assert connection.status == "pending"
        assert connection.compatibility_score > 0
        assert "rock" in connection.shared_genres
        assert "artist2" in connection.shared_artists

    def test_create_duplicate_connection(self, db: Session, test_user, 
                                       test_target_user, test_connection):
        # Setup
        db.add(test_connection)
        db.commit()

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            create_connection(db, test_user.id, test_target_user.id)
        assert exc_info.value.status_code == 400
        assert "Connection already exists" in str(exc_info.value.detail)

    def test_accept_connection(self, db: Session, test_connection):
        # Setup
        db.add(test_connection)
        db.commit()

        # Execute
        updated_connection = accept_connection(db, test_connection.id)

        # Assert
        assert updated_connection.status == "accepted"

    def test_accept_nonexistent_connection(self, db: Session):
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            accept_connection(db, UUID('00000000-0000-0000-0000-000000000000'))
        assert exc_info.value.status_code == 404

    def test_reject_connection(self, db: Session, test_connection):
        # Setup
        db.add(test_connection)
        db.commit()

        # Execute
        updated_connection = reject_connection(db, test_connection.id)

        # Assert
        assert updated_connection.status == "rejected"

    def test_reject_nonexistent_connection(self, db: Session):
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            reject_connection(db, UUID('00000000-0000-0000-0000-000000000000'))
        assert exc_info.value.status_code == 404

    def test_delete_connection(self, db: Session, test_connection):
        # Setup
        db.add(test_connection)
        db.commit()

        # Execute
        delete_connection(db, test_connection.id)

        # Assert
        connection = db.get(Connection, test_connection.id)
        assert connection is None

    def test_delete_nonexistent_connection(self, db: Session):
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            delete_connection(db, UUID('00000000-0000-0000-0000-000000000000'))
        assert exc_info.value.status_code == 404
