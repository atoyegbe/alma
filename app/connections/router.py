from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.users.users import UserService
from app.database.database import get_db
from app.auth.auth import get_authenticated_user
from app.models.models import User, Connection
from app.helpers.router.utils import get_user_service


from .connections import ConnectionService


def get_connection_service(
    db_dependency: Annotated[Session, Depends(get_db)],
    user_serivce: UserService = Depends(get_user_service),
) -> ConnectionService:
    return ConnectionService(db_dependency, user_serivce)


router = APIRouter()


@router.get("", response_model=List[Connection])
async def list_user_connections(
    current_user: User = Depends(get_authenticated_user),
    connection_service: ConnectionService = Depends(get_connection_service),
) -> List[Connection]:
    """Get all connections for the current user"""
    return connection_service.get_user_connections(current_user.id)


@router.post("/request/{target_user_id}")
async def request_connection(
    target_user_id: UUID,
    current_user: User = Depends(get_authenticated_user),
    connection_service: ConnectionService = Depends(get_connection_service),
):
    """Create a connection request"""
    connection = connection_service.create_connection(
        current_user.id, target_user_id)
    return {"message": "Connection request sent", "connection": connection}


@router.post("/accept/{connection_id}")
async def accept_connection_request(
    connection_id: UUID,
    current_user: User = Depends(get_authenticated_user),
    connection_service: ConnectionService = Depends(get_connection_service),
):
    """Accept a connection request"""
    connection = connection_service.accept_connection(
        current_user, connection_id)
    return {"message": "Connection accepted", "connection": connection}


@router.post("/decline/{connection_id}")
async def reject_connection_request(
    connection_id: UUID,
    current_user: User = Depends(get_authenticated_user),
    connection_service: ConnectionService = Depends(get_connection_service),

):
    """Reject a connection request"""
    connection = connection_service.reject_connection(current_user, connection_id)
    return {"message": "Connection rejected", "connection": connection}

