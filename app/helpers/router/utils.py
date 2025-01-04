from typing import Annotated

from fastapi import Depends, Request
from sqlmodel import Session

from app.auth.auth import AuthService
from app.database.database import get_db
from app.users.users import UserService


def get_user_service(
    db_dependency: Annotated[Session, Depends(get_db)],
) -> UserService:
    return UserService(db_dependency)


def get_auth_service(request: Request) -> AuthService:
    if isinstance(request.app.state.auth_service, AuthService):
        return request.app.state.auth_service
    else:
        raise ValueError('Invalid auth client')


def get_authenticated_user(
    auth_service: AuthService = Depends(get_auth_service),
) -> UserService:
    return auth_service.get_current_user()
