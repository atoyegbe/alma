from typing import Optional

from fastapi import HTTPException, Header

from app.database.database import db_dependency
from app.users.users import get_user_by_token
from app.models.models import User


async def get_current_user(auth_token: Optional[str] = Header(None)) -> User:
    """
    Validate user authentication token and return current user
    """
    if not auth_token:
        raise HTTPException(status_code=401, detail="No auth header")

    if not auth_token.startswith("Bearer"):
        raise HTTPException(status_code=401, detail="'Bearer' prefix missing")

    token = auth_token[7:]
    if not token:
        raise HTTPException(status_code=401, detail="No token in auth header")

    db = db_dependency
    try:
        user = get_user_by_token(db, auth_token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        return user
    finally:
        db.close()


def get_header(token: str):
    return {"Authorization": f"Bearer {token}"}
