import logging
from typing import List, Optional, Dict
from uuid import UUID
from fastapi import HTTPException
from sqlmodel import Session, select

from app.recommendation.datamodels import SharedMusic, UserCompatibility
from app.models.models import User, MusicProfile
from app.models.schema import SocialLinks
from app.recommendation.music_recommender import MusicRecommender


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self._recommender = MusicRecommender()

    def get_user(self, user_id: UUID) -> User:
        """Get user by ID"""
        user = self.db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def get_user_by_spotify_id(self, spotify_id: str) -> Optional[User]:
        """Get user by Spotify ID"""
        statement = select(User).where(User.spotify_id == spotify_id)
        return self.db.exec(statement).first()

    def get_user_by_token(self, auth_token: str) -> Optional[User]:
        """Get user by authentication token"""
        statement = select(User).where(User.spotify_token == auth_token)
        return self.db.exec(statement).first()

    def get_music_profile(self, user_id: UUID) -> MusicProfile:
        """Get user's music profile alone"""
        statement = select(MusicProfile).where(MusicProfile.user_id == user_id)
        profile = self.db.exec(statement).first()
        if not profile:
            logging.error(f"Music profile not found for {user_id}")
            raise HTTPException(status_code=404, detail=f"Music profile not found for {user_id}")
        return profile

    def update_user_music_profile(self, user_id: UUID, profile_data: Dict) -> MusicProfile:
        """Update user's music profile"""
        profile = self.get_music_profile(user_id)

        for key, value in profile_data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def update_user(self, user_id: UUID, profile_data: Dict) -> User:
        """Update user profile"""
        user = self.get_user(user_id)

        for key, value in profile_data.items():
            if hasattr(user, key):
                setattr(user, key, value)

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def create_user(self, user_data: Dict) -> User:
        """Create a new user with Spotify data"""
        # Check if user already exists
        existing_user = self.get_user_by_spotify_id(user_data["spotify_id"])
        if existing_user:
            return existing_user

        # Create new user
        user = User(
            spotify_id=user_data.get("spotify_id"),
            email=user_data.get("email"),
            display_name=user_data.get("display_name"),
            spotify_url=user_data.get("spotify_url"),
            spotify_image_url=user_data.get("images", [{}])[0].get("url"),
            country=user_data.get("country"),
            spotify_token=user_data.get("spotify_token"),
            spotify_refresh_token=user_data.get("refresh_token"),
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # Create empty music profile
        profile = MusicProfile(user_id=user.id)
        self.db.add(profile)
        self.db.commit()

        return user

    def update_social_links(self, user_id: UUID, social_links: SocialLinks) -> User:
        """Update user's social media links"""
        user = self.get_user(user_id)
        user.social_links = social_links.model_dump()
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_recommended_users(self, user_id: UUID, limit: int = 10) -> List[User]:
        """Get recommended users based on music taste"""
        # Get current user's profile
        user_profile = self.get_music_profile(user_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User profile not found")

        # Get all other users
        statement = select(User).where(User.id != user_id)
        other_users = self.db.exec(statement).all()

        # Get recommendations using the music recommender
        recommended_users = self._recommender.get_user_recommendations(
            user_profile, other_users, limit=limit
        )

        return recommended_users

    def get_user_compatibility(
        self, profile1: MusicProfile, profile2: MusicProfile
    ) -> UserCompatibility:
        """Get detailed compatibility analysis between two user profiles"""
        # Get target user's profile
        statement = select(MusicProfile).where(MusicProfile.user_id == user_id)
        target_profile = db.exec(statement).first()
        if not target_profile:
            raise HTTPException(
                status_code=404, detail="Target user's music profile not found"
            )

        # Get current user's profile
        statement = select(MusicProfile).where(MusicProfile.user_id == current_user.id)
        current_profile = db.exec(statement).first()
        if not current_profile:
            raise HTTPException(
                status_code=404, detail="Current user's music profile not found"
            )

        # Calculate compatibility
        similarity = self._recommender.calculate_overall_similarity(
            current_profile.to_dict(), target_profile.to_dict()
        )

        # Add shared music details
        shared_music = self._get_shared_music(current_profile, target_profile)

        return UserCompatibility(
            overall_similarity=similarity.overall_similarity,
            genre_similarity=similarity.genre_similarity,
            artist_similarity=similarity.artist_similarity,
            diversity_similarity=similarity.diversity_similarity,
            obscurity_similarity=similarity.obscurity_similarity,
            decade_similarity=similarity.decade_similarity,
            listening_pattern_similarity=similarity.listening_pattern_similarity,
            shared_music=shared_music,
        )

    def _get_shared_music(self, profile1: MusicProfile, profile2: MusicProfile) -> SharedMusic:
        """Calculate shared music between two profiles."""
        shared_music = SharedMusic(
            artists=list(set(profile1.top_artists) & set(profile2.top_artists)),
            tracks=list(set(profile1.top_tracks) & set(profile2.top_tracks)),
            genres=list(set(profile1.genres) & set(profile2.genres)),
        )
        return shared_music
