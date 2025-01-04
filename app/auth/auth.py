from typing import Optional

from fastapi import HTTPException, Header
from sqlmodel import Session, select

from app.models.models import User


class AuthService():
    def __init__(self, db: Session):
        self.db = db

    def get_current_user(
            self,
            auth_token: Optional[str] = Header(None)
            ) -> User:
        """
        Validate user authentication token and return current user
        """
        if not auth_token:
            raise HTTPException(status_code=401, detail="No auth header")

        auth_token = str(auth_token)
        if not auth_token.startswith("Bearer"):
            raise HTTPException(status_code=401, detail="'Bearer' prefix missing")

        token = auth_token[7:]
        if not token:
            raise HTTPException(status_code=401, detail="No token in auth header")

        user = self.get_user_by_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        return user

    def get_user_by_token(self, auth_token: str) -> Optional[User]:
        """Get user by authentication token"""
        statement = select(User).where(User.spotify_token == auth_token)
        return self.db.exec(statement).first()
