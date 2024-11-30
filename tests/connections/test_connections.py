import pytest
from uuid import UUID, uuid4
from fastapi import HTTPException
from sqlmodel import Session, select
import json

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
def test_music_profile(test_user) -> MusicProfile:
    """Create a test music profile"""
    return MusicProfile(
        user_id=test_user.id,
        top_artists=["wizkid", "drake", "beyonce"],
        top_tracks=["bend", "blinding lights", "lovely", "bad guy"],
        genres=["rock", "pop", "hip-hop", "afrobeats", "afropop"],
        favorite_decades=["80s", "90s", "00s"],
        preferred_genres=["rock"],
        discovery_preferences={"new_releases": True},
        listening_history=[{"track": "track1", "timestamp": "2021-01-01"}],
        energy_score=0.8,
        danceability_score=0.7,
        diversity_score=0.6,
        obscurity_score=0.5
    )

@pytest.fixture
def test_target_music_profile(test_target_user) -> MusicProfile:
    """Create a test target music profile"""
    return MusicProfile(
        user_id=test_target_user.id,
        top_artists=["wizkid", "drake"],
        top_tracks=["bend", "blinding lights"],
        genres=["rock", "jazz", "afrobeats", "afropop"],
        favorite_decades=["90s", "00s"],
        preferred_genres=["jazz"],
        discovery_preferences={"new_releases": False},
        energy_score=0.7,
        danceability_score=0.6,
        diversity_score=0.5,
        obscurity_score=0.4
    )

@pytest.fixture
def test_connection(test_user, test_target_user) -> Connection:
    """Create a test connection"""
    return Connection(
        id=uuid4(),
        user_id=test_user.id,
        connected_user_id=test_target_user.id,
        status="pending",
        overall_compatibility=0.8,
        compatibility_breakdown={
            "genre_match": 0.8,
            "artist_match": 0.7
        },
        shared_genres=["rock"],
        shared_artists=["artist2"]
    )

class TestConnections:
    @pytest.fixture(autouse=True)
    def setup(self, db: Session, test_user, test_target_user):
        """Setup fixture that runs automatically before each test method"""
        db.add(test_user)
        db.add(test_target_user)
        db.commit()
        
    def test_get_user_connections(self, db: Session, test_user, test_target_user, test_connection):
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
        db.add(test_music_profile)
        db.add(test_target_music_profile)
        db.commit()
        # Execute
        connection = create_connection(db, test_user.id, test_target_user.id)

        # Assert
        assert connection.user_id == test_user.id
        # assert connection.connected_user_id == test_target_user.id
        # assert connection.status == "pending"
        # assert connection.compatibility_score > 0
        # assert "rock" in connection.shared_genres
        # assert "artist2" in connection.shared_artists

    # def test_create_duplicate_connection(self, db: Session, test_user, 
    #                                    test_target_user, test_connection):
    #     # Setup
    #     db.add(test_connection)
    #     db.commit()

    #     # Execute & Assert
    #     with pytest.raises(HTTPException) as exc_info:
    #         create_connection(db, test_user.id, test_target_user.id)
    #     assert exc_info.value.status_code == 400
    #     assert "Connection already exists" in str(exc_info.value.detail)

    # def test_accept_connection(self, db: Session, test_connection):
    #     # Setup
    #     db.add(test_connection)
    #     db.commit()

    #     # Execute
    #     updated_connection = accept_connection(db, test_connection.id)

    #     # Assert
    #     assert updated_connection.status == "accepted"

    # def test_accept_nonexistent_connection(self, db: Session):
    #     # Execute & Assert
    #     with pytest.raises(HTTPException) as exc_info:
    #         accept_connection(db, UUID('00000000-0000-0000-0000-000000000000'))
    #     assert exc_info.value.status_code == 404

    # def test_reject_connection(self, db: Session, test_connection):
    #     # Setup
    #     db.add(test_connection)
    #     db.commit()

    #     # Execute
    #     updated_connection = reject_connection(db, test_connection.id)

    #     # Assert
    #     assert updated_connection.status == "rejected"

    # def test_reject_nonexistent_connection(self, db: Session):
    #     # Execute & Assert
    #     with pytest.raises(HTTPException) as exc_info:
    #         reject_connection(db, UUID('00000000-0000-0000-0000-000000000000'))
    #     assert exc_info.value.status_code == 404

    # def test_delete_connection(self, db: Session, test_connection):
    #     # Setup
    #     db.add(test_connection)
    #     db.commit()

    #     # Execute
    #     delete_connection(db, test_connection.id)

    #     # Assert
    #     connection = db.get(Connection, test_connection.id)
    #     assert connection is None

    # def test_delete_nonexistent_connection(self, db: Session):
    #     # Execute & Assert
    #     with pytest.raises(HTTPException) as exc_info:
    #         delete_connection(db, UUID('00000000-0000-0000-0000-000000000000'))
    #     assert exc_info.value.status_code == 404
