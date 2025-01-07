import uuid
import pytest

from app.users.users import UserService
from app.models.models import User


@pytest.mark.dependency()
async def test_create_profile(
    sample_user,
    other_sample_user,
    get_other_sample_user_profile
):
    assert sample_user is not None
    assert other_sample_user is not None
    assert get_other_sample_user_profile is not None


@pytest.mark.dependency(depends=["test_create_profile"])
@pytest.mark.asyncio
async def test_get_compatibility_success(
    client,
    other_sample_user: User,
):
    response = await client.get(
        f"/recommendations/compatibility/{other_sample_user.id}"
    )

    # Assert
    assert response.status_code == 200
    # data = response.json()
    # assert "overall_similarity" in data
    # assert "shared_music" in data
    # assert len(data["shared_music"]["artists"]) > 0  # Should have shared artist2
    # assert len(data["shared_music"]["tracks"]) > 0  # Should have shared track2
    # assert len(data["shared_music"]["genres"]) > 0  # Should have shared genres


@pytest.mark.asyncio
async def test_unauthorized_user_access(client):
    response = await client.get("/recommendations/users",
                                headers={'auth-token': 'rubbissshhh'})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_invalid_user_id(
    client,
):
    invalid_user_id = uuid.uuid4()
    response = await client.get(
        f"/recommendations/compatibility/{invalid_user_id}"
    )
    assert response.status_code == 404
