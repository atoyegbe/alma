from typing import Annotated

from fastapi import Depends, Request
from sqlmodel import Session

from alma.app.auth.auth import AuthService
from alma.app.database.database import get_db
from alma.app.users.users import UserService


def get_user_service(
    db_dependency: Annotated[Session, Depends(get_db)],
) -> UserService:
    return UserService(db_dependency)


def get_auth_service(request: Request) -> AuthService:
    if isinstance(request.app.state.auth_service, AuthService):
        return request.app.state.auth_service
    else:
        raise ValueError('Invalid auth client')
