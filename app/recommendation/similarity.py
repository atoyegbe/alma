
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models.models import User


def get_users_similiraity(user1: User, user2: User) -> float:
    # Combine user profile attributes into lists
    user1_profile = [user1.genres, user1.top_tracks, user1.top_artists]
    user2_profile = [user2.genres, user2.top_tracks, user2.top_artists]

    # Combine user profiles into strings for TF-IDF
    user1_profile_strings = [' '.join(profile) for profile in user1_profile]
    user2_profile_strings = [' '.join(profile) for profile in user2_profile]

    # Initialize TF-IDF Vectorizer
    vectorizer = TfidfVectorizer()

    # Fit and transform user profiles
    tfidf_matrix = vectorizer.fit_transform(user1_profile_strings + user2_profile_strings)

    # Calculate cosine similarity using sklearn.metrics.pairwise.cosine_similarity
    cosine_similarity_score = cosine_similarity(tfidf_matrix)[0][1]

    return cosine_similarity_score


