from typing import List, Dict, Any
from datetime import datetime
import statistics
from collections import Counter

from app.models.schema import Metrics


class MusicProfileAnalyzer:
    def __init__(self, spotify_client):
        self.spotify = spotify_client

    async def analyze_favorite_decades(self, tracks: List[Dict[str, Any]]) -> List[str]:
        """Calculate favorite decades based on track release dates and popularity"""
        decade_counts = Counter()

        for track in tracks:
            release_date = track.get("album", {}).get("release_date")
            if not release_date:
                continue

            try:
                year = int(release_date[:4])
                decade = f"{(year // 10) * 10}s"  # e.g., 1980 -> "80s"
                # Weight by track popularity
                weight = track.get("popularity", 50) / 50  # Normalize to 0-2 range
                decade_counts[decade] += weight
            except (ValueError, TypeError):
                continue

        # Return top 3 decades
        return [decade for decade, _ in decade_counts.most_common(3)]

    async def analyze_listening_patterns(
        self, recent_tracks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze listening patterns from recent tracks"""
        patterns = {
            "by_hour": Counter(),
            "by_day": Counter(),
            "by_genre": Counter(),
            "most_played": Counter(),
            "recent_tracks": [],
        }

        for track in recent_tracks:
            # Extract basic track info
            track_data = track.get("track", {})
            played_at = track.get("played_at")

            if not played_at or not track_data:
                continue

            # Parse timestamp
            try:
                played_time = datetime.fromisoformat(played_at.replace('Z', '+00:00'))
                patterns["by_hour"][played_time.hour] += 1
                patterns["by_day"][played_time.strftime("%A")] += 1
            except (ValueError, TypeError):
                continue

            # Track play count
            track_id = track_data.get("id")
            if track_id:
                patterns["most_played"][track_id] += 1

            # Genre analysis (requires additional API call)
            artist_id = track_data.get("artists", [{}])[0].get("id")
            if artist_id:
                artist_data = await self.spotify.artist(artist_id)
                for genre in artist_data.get("genres", []):
                    patterns["by_genre"][genre] += 1

            # Add to recent tracks
            patterns["recent_tracks"].append(
                {
                    "id": track_data.get("id"),
                    "name": track_data.get("name"),
                    "artist": track_data.get("artists", [{}])[0].get("name"),
                    "played_at": played_at,
                }
            )

        # Convert counters to dictionaries
        return {
            "by_hour": dict(patterns["by_hour"]),
            "by_day": dict(patterns["by_day"]),
            "by_genre": dict(patterns["by_genre"].most_common(10)),  # Top 10 genres
            "most_played": dict(
                patterns["most_played"].most_common(10)
            ),  # Top 10 tracks
            "recent_tracks": patterns["recent_tracks"][-20:],  # Last 20 tracks
        }

    async def calculate_energy_score(self, audio_features: List[Dict[str, Any]]) -> int:
        """Calculate energy score from audio features"""
        if not audio_features:
            return 50  # Default score

        valid_features = [f for f in audio_features if f and "energy" in f]
        if not valid_features:
            return 50

        return int(
            sum(track["energy"] * 100 for track in valid_features) / len(valid_features)
        )

    async def calculate_danceability_score(
        self, audio_features: List[Dict[str, Any]]
    ) -> int:
        """Calculate danceability score from audio features"""
        if not audio_features:
            return 50

        valid_features = [f for f in audio_features if f and "danceability" in f]
        if not valid_features:
            return 50

        return int(
            sum(track["danceability"] * 100 for track in valid_features)
            / len(valid_features)
        )

    async def calculate_diversity_score(
        self,
        genres: List[str],
        artists: List[Dict[str, Any]],
        audio_features: List[Dict[str, Any]],
    ) -> int:
        """
        Calculate diversity score based on:
        - Genre diversity
        - Artist diversity
        - Audio feature diversity
        """
        # Genre diversity (33.33%)
        unique_genres = set(genres)
        genre_score = min(len(unique_genres) / 30 * 100, 100)  # Cap at 100

        # Artist diversity (33.33%)
        artist_genres = set()
        for artist in artists:
            artist_genres.update(artist.get("genres", []))
        artist_score = min(len(artist_genres) / 50 * 100, 100)

        # Audio feature diversity (33.33%)
        feature_scores = []
        if audio_features:
            for feature in ["tempo", "energy", "valence", "danceability"]:
                values = [track.get(feature, 0) for track in audio_features if track]
                if values:
                    try:
                        # Higher standard deviation = more diversity
                        std = statistics.stdev(values)
                        # Normalize std to 0-100 scale (typical std ranges from 0-0.3)
                        feature_scores.append(min(std * 333, 100))
                    except statistics.StatisticsError:
                        continue

        feature_score = (
            sum(feature_scores) / len(feature_scores) if feature_scores else 50
        )

        # Combine scores
        return int((genre_score + artist_score + feature_score) / 3)

    async def calculate_obscurity_score(
        self, artists: List[Dict[str, Any]], tracks: List[Dict[str, Any]]
    ) -> int:
        """
        Calculate obscurity score based on:
        - Artist popularity
        - Track popularity
        - Ratio of mainstream to niche artists
        """
        # Artist obscurity (40%)
        artist_scores = [
            100 - artist.get("popularity", 50) for artist in artists if artist
        ]
        artist_obscurity = (
            sum(artist_scores) / len(artist_scores) if artist_scores else 50
        )

        # Track obscurity (40%)
        track_scores = [100 - track.get("popularity", 50) for track in tracks if track]
        track_obscurity = sum(track_scores) / len(track_scores) if track_scores else 50

        # Mainstream ratio (20%)
        mainstream_threshold = (
            70  # Artists with popularity > 70 are considered mainstream
        )
        mainstream_count = sum(
            1
            for artist in artists
            if artist.get("popularity", 0) > mainstream_threshold
        )
        mainstream_ratio = mainstream_count / len(artists) if artists else 0.5
        mainstream_score = 100 - (mainstream_ratio * 100)  # Lower ratio = higher score

        # Weighted average
        return int(
            (artist_obscurity * 0.4)
            + (track_obscurity * 0.4)
            + (mainstream_score * 0.2)
        )

    async def get_complete_profile_metrics(self) -> Metrics:
        """
        Calculate all profile metrics in one go.
        Returns a complete profile including all metrics and patterns.
        """
        # Get all necessary data
        top_tracks = await self.spotify.current_user_top_tracks(
            limit=50, time_range="long_term"
        )
        top_artists = await self.spotify.current_user_top_artists(
            limit=50, time_range="long_term"
        )
        recent_tracks = await self.spotify.current_user_recently_played(limit=50)

        # Get audio features for top tracks
        track_ids = [track["id"] for track in top_tracks.get("items", [])]
        audio_features = (
            await self.spotify.audio_features(track_ids) if track_ids else []
        )

        # Extract genres from top artists
        genres = [
            genre
            for artist in top_artists.get("items", [])
            for genre in artist.get("genres", [])
        ]

        # Calculate all metrics
        metrics = {
            "favorite_decades": await self.analyze_favorite_decades(
                top_tracks.get("items", [])
            ),
            "listening_pattern_similarity": await self.analyze_listening_patterns(
                recent_tracks.get("items", [])
            ),
            "energy_score": await self.calculate_energy_score(audio_features),
            "danceability_score": await self.calculate_danceability_score(
                audio_features
            ),
            "diversity_score": await self.calculate_diversity_score(
                genres, top_artists.get("items", []), audio_features
            ),
            "obscurity_score": await self.calculate_obscurity_score(
                top_artists.get("items", []), top_tracks.get("items", [])
            ),
        }

        return Metrics(**metrics)
