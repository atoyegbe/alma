from uuid import uuid4
import pytest


@pytest.mark.usefixtures('event_loop')
class TestRecommendationEndpoints:
    # async def test_get_recommendations_success(
    #     self,
    #     client,
    # ):
    #     response = await client.get(
    #         "/recommendations/users",
    #     )
    #     # Assert
    #     assert response.status_code == 200
    #     data = response.json()
    #     assert isinstance(data, list)
    #     assert len(data) <= 10  # Default limit

    #     if data:
    #         first_rec = data[0]
    #         assert "user_id" in first_rec
    #         assert "similarity_score" in first_rec
    #         assert "compatibility" in first_rec

    #         compatibility = first_rec["compatibility"]
    #         assert "overall_similarity" in compatibility
    #         assert "genre_similarity" in compatibility
    #         assert "shared_music" in compatibility

    # def test_get_recommendations_with_filters(
    #     self,
    #     client: TestClient,
    #     db: Session,
    #     test_user,
    #     test_user_profile,
    #     other_users,
    #     other_profiles,
    # ):
    #     # Setup
    #     db.add(test_user)
    #     db.add(test_user_profile)
    #     for user, profile in zip(other_users, other_profiles):
    #         db.add(user)
    #         db.add(profile)
    #     db.commit()

    #     # Test with query parameters
    #     response = client.get(
    #         "/recommendations/users",
    #         params={"limit": 2, "min_score": 0.5, "genres": ["rock", "indie"]},
    #         headers={"auth_token": f"Bearer {test_user.spotify_token}"},
    #     )

    #     # Assert
    #     assert response.status_code == 200
    #     data = response.json()
    #     assert len(data) <= 2
    #     for rec in data:
    #         assert rec["similarity_score"] >= 0.5
    #         shared_genres = rec["compatibility"]["shared_music"]["genres"]
    #         assert any(genre in shared_genres for genre in ["rock", "indie"])

    # def test_get_recommendations_no_profile(
    #     self, db_test, sample_user, client
    # ):
    #     # Setup
    #     db_test.add(sample_user)
    #     db_test.commit()

    #     # Execute
    #     response = client.get(
    #         "/recommendations/users",
    #     )

    #     # Assert
    #     assert response.status_code == 404
    #     assert "Music profile not found" in response.json()["detail"]

    # def test_get_compatibility_success(
    #     self,
    #     client: TestClient,
    #     db: Session,
    #     test_user,
    #     test_user_profile,
    #     other_users,
    #     other_profiles,
    # ):
    #     # Setup
    #     db.add(test_user)
    #     db.add(test_user_profile)
    #     target_user = other_users[0]
    #     target_profile = other_profiles[0]
    #     db.add(target_user)
    #     db.add(target_profile)
    #     db.commit()

    #     # Execute
    #     response = client.get(
    #         f"/recommendations/compatibility/{target_user.id}",
    #         headers={"auth_token": f"Bearer {test_user.spotify_token}"},
    #     )

    #     # Assert
    #     assert response.status_code == 200
    #     data = response.json()
    #     assert "overall_similarity" in data
    #     assert "shared_music" in data
    #     assert len(data["shared_music"]["artists"]) > 0  # Should have shared artist2
    #     assert len(data["shared_music"]["tracks"]) > 0  # Should have shared track2
    #     assert len(data["shared_music"]["genres"]) > 0  # Should have shared genres

    # def test_get_compatibility_with_self(
    #     self, client: TestClient, db: Session, test_user, test_user_profile
    # ):
    #     # Setup
    #     db.add(test_user)
    #     db.add(test_user_profile)
    #     db.commit()

    #     # Execute
    #     response = client.get(
    #         f"/recommendations/compatibility/{test_user.id}",
    #         headers={"auth_token": f"Bearer {test_user.spotify_token}"},
    #     )

    #     # Assert
    #     assert response.status_code == 400
    #     assert "Cannot calculate compatibility with self" in response.json()["detail"]

    # def test_unauthorized_access(self, client: TestClient):
    #     # Test recommendations endpoint
    #     response = client.get("/recommendations/users")
    #     assert response.status_code == 401

    #     # Test compatibility endpoint
    #     response = client.get(f"/recommendations/compatibility/{uuid4()}")
    #     assert response.status_code == 401

    async def test_invalid_user_id(
        self, client
    ):
        response = await client.get(
            f"/recommendations/compatibility/{uuid4()}",
        )

        # Assert
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
