from typing import Dict, Any, Optional

from sqlalchemy.orm import Session

from app.models import User
from app.schema import UserSchema


def create_user(db: Session, user: UserSchema):
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: str):
    return db.query(User).filter(User.user_id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


def get_user_friends(db: Session, user_id: str):
    user: User = db.query(User).filter(User.user_id == user_id).first()
    return user.friends


def update_user(db: Session, user_id: int, **kwargs) -> None:
    """
    Updates one or more fields of a user with the given ID.

    Args:
        session: The SQLAlchemy session to use.
        user_id: The ID of the user to update.
        **kwargs: Keyword arguments representing the fields to update and their new values.
    """

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise ValueError(f"User with id {user_id} not found.")

    for field, value in kwargs.items():
        setattr(user, field, value)

    db.commit()
    return user

