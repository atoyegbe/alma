from typing import Dict, List, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class MusicRecommender:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        
    def calculate_text_similarity(self, text1: List[str], text2: List[str]) -> float:
        """Calculate cosine similarity between two lists of text items"""
        if not text1 or not text2:
            return 0.0
            
        # Join items into strings
        text1_str = " ".join(str(item) for item in text1)
        text2_str = " ".join(str(item) for item in text2)
        
        # Fit and transform the texts
        tfidf_matrix = self.vectorizer.fit_transform([text1_str, text2_str])
        
        # Calculate cosine similarity
        return cosine_similarity(tfidf_matrix)[0][1]

    def calculate_numeric_similarity(self, score1: float, score2: float) -> float:
        """Calculate similarity between two numeric scores"""
        if score1 is None or score2 is None:
            return 0.0
        return 1 - abs(score1 - score2)
        
    def calculate_listening_patterns_similarity(
        self,
        user1_patterns: Dict[str, Any],
        user2_patterns: Dict[str, Any]
    ) -> float:
        """Calculate similarity based on listening patterns"""
        if not user1_patterns or not user2_patterns:
            return 0.0
            
        # Compare hour distributions
        hours1 = user1_patterns.get("by_hour", {})
        hours2 = user2_patterns.get("by_hour", {})
        
        if hours1 and hours2:
            hour_vector1 = [hours1.get(str(h), 0) for h in range(24)]
            hour_vector2 = [hours2.get(str(h), 0) for h in range(24)]
            return cosine_similarity([hour_vector1], [hour_vector2])[0][0]
            
        return 0.0

    def calculate_overall_similarity(self, profile1: Dict[str, Any], profile2: Dict[str, Any]) -> Dict[str, float]:
        """Calculate overall similarity between two user profiles with detailed breakdown"""
        similarities = {}
        
        # Genre similarity using cosine similarity
        genres1 = profile1.get("genres", [])
        genres2 = profile2.get("genres", [])
        similarities["genre_similarity"] = self.calculate_text_similarity(genres1, genres2)
        
        # Artist similarity using cosine similarity
        artists1 = [artist["name"] for artist in profile1.get("top_artists", [])]
        artists2 = [artist["name"] for artist in profile2.get("top_artists", [])]
        similarities["artist_similarity"] = self.calculate_text_similarity(artists1, artists2)
        
        # Track similarity using cosine similarity
        tracks1 = [track["name"] for track in profile1.get("top_tracks", [])]
        tracks2 = [track["name"] for track in profile2.get("top_tracks", [])]
        similarities["track_similarity"] = self.calculate_text_similarity(tracks1, tracks2)
        
        # Numeric profile metrics similarity
        metric_pairs = [
            ("energy_similarity", "energy_score"),
            ("danceability_similarity", "danceability_score"),
            ("diversity_similarity", "diversity_score"),
            ("obscurity_similarity", "obscurity_score")
        ]
        
        for sim_key, metric_key in metric_pairs:
            similarities[sim_key] = self.calculate_numeric_similarity(
                profile1.get(metric_key, 0.0),
                profile2.get(metric_key, 0.0)
            )
        
        # Decade preference similarity
        decades1 = profile1.get("favorite_decades", [])
        decades2 = profile2.get("favorite_decades", [])
        similarities["decade_similarity"] = self.calculate_text_similarity(
            [str(d) for d in decades1],
            [str(d) for d in decades2]
        )
        
        # Listening patterns similarity
        similarities["listening_patterns"] = self.calculate_listening_patterns_similarity(
            profile1.get("listening_history", {}),
            profile2.get("listening_history", {})
        )
        
        # Calculate weighted overall similarity
        weights = {
            "genre_similarity": 0.20,
            "artist_similarity": 0.20,
            "track_similarity": 0.15,
            "energy_similarity": 0.07,
            "danceability_similarity": 0.07,
            "diversity_similarity": 0.07,
            "obscurity_similarity": 0.07,
            "decade_similarity": 0.07,
            "listening_patterns": 0.10
        }
        
        overall_similarity = sum(
            similarities[key] * weight 
            for key, weight in weights.items()
        )
        
        return {
            "overall_similarity": overall_similarity,
            "component_similarities": similarities
        }

    def get_user_recommendations(
        self, target_profile: Dict[str, Any], other_profiles: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Get recommended users sorted by similarity score"""
        recommendations = []
        
        for profile in other_profiles:
            similarity_result = self.calculate_overall_similarity(target_profile, profile)
            recommendations.append({
                "user_id": profile["id"],
                "similarity_score": similarity_result["overall_similarity"],
                "similarity_breakdown": similarity_result["component_similarities"]
            })
        
        # Sort by similarity score in descending order
        recommendations.sort(key=lambda x: x["similarity_score"], reverse=True)
        return recommendations
