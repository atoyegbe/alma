from typing import List
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session, select, and_

from app.users.users import UserService
from app.recommendation.music_recommender import MusicRecommender
from app.models.models import Connection, User


class ConnectionService:
    def __init__(
            self,
            db: Session,
            user_service: UserService
    ):
        self.db = db
        self.user_service = user_service
        self.recommender = MusicRecommender()

    def get_user_connections(self, user_id: UUID) -> List[Connection]:
        """Get connections for a user"""
        statement = select(Connection).where(Connection.user_id == user_id)
        return self.db.exec(statement).all()

    def create_connection(
            self,
            user_id: UUID,
            target_user_id: UUID
            ) -> Connection:
        """Create a connection between two users"""
        # Check if connection already exists
        statement = select(Connection).where(
            and_(
                Connection.user_id == user_id,
                Connection.connected_user_id == target_user_id,
            )
        )
        existing_connection = self.db.exec(statement).first()
        if existing_connection:
            raise HTTPException(status_code=400, detail="Connection already exists")

        # Get both users' music profiles
        current_user_profile = self.user_service.get_music_profile(user_id)
        target_profile = self.user_service.get_music_profile(target_user_id)

        if not current_user_profile or not target_profile:
            raise HTTPException(status_code=404, detail="Music profile not found")

            # TODO: : we probably don't need to calculate compatability at this point
        # we are alreadysending compatability when recommending users in `/recommendations/users` endpoint
        # Calculate compatibility score
        current_profile_dict = current_user_profile.dict()
        target_profile_dict = target_profile.dict()
        compatibility = self.recommender.calculate_overall_similarity(
            current_profile_dict, target_profile_dict
        )

        # Find shared music elements
        shared_genres = list(set(current_user_profile.genres) & set(target_profile.genres))
        shared_artists = list(
            set(current_user_profile.top_artists) & set(target_profile.top_artists)
        )
        shared_tracks = list(
            set(current_user_profile.top_tracks) & set(target_profile.top_tracks)
        )

        # Create new connection
        new_connection = Connection(
            user_id=user_id,
            connected_user_id=target_user_id,
            status="pending",
            overall_compatibility=int(compatibility.overall_similarity * 100),
            compatibility_breakdown=compatibility.dict(),
            shared_genres=shared_genres,
            shared_artists=shared_artists,
            shared_tracks=shared_tracks,
        )

        # Add connection to database
        self.db.add(new_connection)
        self.db.commit()
        self.db.refresh(new_connection)
        return new_connection

    def accept_connection(
            self,
            current_user: User, connection_id: UUID) -> Connection:
        """Accept a connection request"""
        statement = select(Connection).where(
            and_(
                Connection.user_id == current_user.id,
                Connection.id == connection_id
            )
        )
        connection = self.db.exec(statement).first()
        if not connection:
            raise HTTPException(status_code=400, detail="Connection not found")

        connection.status = "accepted"
        self.db.add(connection)
        self.db.commit()
        self.db.refresh(connection)
        return connection

    def reject_connection(self, current_user: User, connection_id: UUID) -> Connection:
        """Reject a connection request"""
        statement = select(Connection).where(
            and_(
                Connection.user_id == current_user.id,
                Connection.id == connection_id
            )
        )
        connection = self.db.exec(statement).first()
        if not connection:
            raise HTTPException(status_code=400, detail="Connection not found")

        connection.status = "rejected"
        self.db.add(connection)
        self.db.commit()
        self.db.refresh(connection)
        return connection

    def delete_connection(self, current_user: User, connection_id: UUID):
        """Delete a connection"""
        statement = select(Connection).where(
            and_(
                Connection.user_id == current_user.id,
                Connection.id == connection_id
            )
        )
        connection = self.db.exec(statement).first()
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")

        self.db.delete(connection)
        self.db.commit()



# def get_user_connections(db: Session, user_id: UUID) -> List[Connection]:
#     """Get connections for a user"""
#     statement = select(Connection).where(Connection.user_id == user_id)
#     return db.exec(statement).all()


# def create_connection(db: Session, user_id: UUID, target_user_id: UUID) -> Connection:
#     """Create a connection between two users"""
#     # Check if connection already exists
#     statement = select(Connection).where(
#         and_(
#             Connection.user_id == user_id,
#             Connection.connected_user_id == target_user_id,
#         )
#     )
#     existing = db.exec(statement).first()
#     if existing:
#         raise HTTPException(status_code=400, detail="Connection already exists")

#     # Get both users' music profiles
#     user_profile_statement = select(MusicProfile).where(MusicProfile.user_id == user_id)
#     target_profile_statement = select(MusicProfile).where(
#         MusicProfile.user_id == target_user_id
#     )
#     print('got here')

#     current_profile = db.exec(statement=user_profile_statement).first()
#     target_profile = db.exec(statement=target_profile_statement).first()

#     if not current_profile or not target_profile:
#         raise HTTPException(status_code=404, detail="Music profile not found")
    
#     print('passed here')


#     # TODO: : we probably don't need to calculate compatability at this point
#     # we are alreadysending compatability when recommending users in `/recommendations/users` endpoint
#     # Calculate compatibility score
#     current_profile_dict = current_profile.dict()
#     target_profile_dict = target_profile.dict()
#     compatibility = recommender.calculate_overall_similarity(
#         current_profile_dict, target_profile_dict
#     )

#     # Find shared music elements
#     shared_genres = list(set(current_profile.genres) & set(target_profile.genres))
#     shared_artists = list(
#         set(current_profile.top_artists) & set(target_profile.top_artists)
#     )
#     shared_tracks = list(
#         set(current_profile.top_tracks) & set(target_profile.top_tracks)
#     )

#     # Create new connection
#     new_connection = Connection(
#         user_id=user_id,
#         connected_user_id=target_user_id,
#         status="pending",
#         overall_compatibility=int(compatibility.overall_similarity * 100),
#         compatibility_breakdown=compatibility.dict(),
#         shared_genres=shared_genres,
#         shared_artists=shared_artists,
#         shared_tracks=shared_tracks,
#     )

#     # Add connection to database
#     db.add(new_connection)
#     db.commit()
#     db.refresh(new_connection)
#     return new_connection


# def accept_connection(db: Session, connection_id: UUID) -> Connection:
#     """Accept a connection request"""
#     statement = select(Connection).where(Connection.id == connection_id)
#     connection = db.exec(statement).first()
#     if not connection:
#         raise HTTPException(status_code=404, detail="Connection not found")

#     connection.status = "accepted"
#     db.add(connection)
#     db.commit()
#     db.refresh(connection)
#     return connection


# def reject_connection(db: Session, connection_id: UUID) -> Connection:
#     """Reject a connection request"""
#     statement = select(Connection).where(Connection.id == connection_id)
#     connection = db.exec(statement).first()
#     if not connection:
#         raise HTTPException(status_code=404, detail="Connection not found")

#     connection.status = "rejected"
#     db.add(connection)
#     db.commit()
#     db.refresh(connection)
#     return connection


# def delete_connection(db: Session, connection_id: UUID) -> None:
#     """Delete a connection"""
#     statement = select(Connection).where(Connection.id == connection_id)
#     connection = db.exec(statement).first()
#     if not connection:
#         raise HTTPException(status_code=404, detail="Connection not found")

#     db.delete(connection)
#     db.commit()
#     return {"message": "Connection deleted"}
