import uuid
from fastapi import HTTPException
import pytest

from app.models.models import User


@pytest.mark.asyncio
class TestConnectionRequests:
    _connection_id = None

    async def test_send_request_connections(
            self,
            client,
            other_sample_user: User,
    ):
        response = await client.post(
            f"/connections/request/{other_sample_user.id}")
        assert response.status_code == 200
        data = response.json()
        assert data['message'] == "Connection request sent"
        assert data['connection']['status'] == "pending"
        assert data['connection']['connected_user_id'] == str(other_sample_user.id)
        assert 'overall_compatibility' in data['connection']

    @pytest.mark.dependency(
            depends=["TestConnectionRequests::test_send_request_connections"])
    async def test_send_duplicate_request_connection(
        self,
        client,
        other_sample_user: User,
    ):
        response = await client.post(
                f"/connections/request/{other_sample_user.id}")
        assert response.status_code == 400
        assert "Connection already exists" == response.json()['detail']

    async def test_get_user_connections(
            self,
            client,
    ):
        response = await client.get("/connections")
        assert response.status_code == 200
        data = response.json()

        assert len(data) >= 1
        connections = data[0]
        TestConnectionRequests._connection_id = connections['id']

    @pytest.mark.dependency(
            depends=["TestConnectionRequests::test_send_request_connections"])
    async def test_accept_connection(
            self,
            client,
            ):
        connect_id = TestConnectionRequests._connection_id
        response = await client.post(
            f"/connections/accept/{connect_id}")

        # Assert
        assert response.status_code == 200

        data = response.json()
        updated_connection = data['connection']
        assert updated_connection['status'] == "accepted"

    async def test_accept_nonexistent_connection(
        self,
        client
    ):
        non_existence_id = uuid.uuid4()
        response = await client.post(
            f"/connections/accept/{non_existence_id}")

        # Assert
        assert response.status_code == 400
        assert "Connection not found" == response.json()['detail']

    @pytest.mark.dependency(
        depends=["TestConnectionRequests::test_send_request_connections"])
    async def test_reject_connection(
            self,
            client,
    ):
        connect_id = TestConnectionRequests._connection_id
        response = await client.post(
            f"/connections/decline/{connect_id}")

        # Assert
        assert response.status_code == 200

        data = response.json()
        updated_connection = data['connection']
        assert updated_connection['status'] == "rejected"

    @pytest.mark.dependency(
            depends=["TestConnectionRequests::test_send_request_connections"])
    async def test_cancel_connection(
            self,
            client,
            ):
        connect_id = TestConnectionRequests._connection_id
        response = await client.post(
            f"/connections/cancel/{connect_id}")

        # Assert
        assert response.status_code == 200

        assert "Connection cancelled" == response.json()['message']

