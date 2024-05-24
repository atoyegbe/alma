import logging
from typing import Any, Dict, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import User
from app.schema import UserData, UserSchema

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def user_to_dict(user):
    user_dict = {
        "user_id": user.user_id,
        "username": user.username,
        "country": user.country,
        "genres": user.genres,
        "top_artists": user.top_artists,
        "top_tracks": user.top_tracks,
        "top_albums": user.top_albums,
        "created_at": user.created_at,
    }
    return user_dict


async def create_user(db: Session, user: UserSchema):
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


async def get_user(db: Session, user_id: str):
    return db.query(User).filter(User.user_id == user_id).first()

async def get_user_by_token(db: Session, token: str) -> Optional[User]:
   user: User = db.query(User).filter(User.auth_token == token).first()
   if not user:
       return None
   return user

async def get_users(db: Session, skip: int = 0, limit: int = 100, **filters):
    query = db.query(User).offset(skip).limit(limit)
    filter_conditions = []

    for field, value in filters.items():
        if hasattr(User, field):
            filter_conditions.append(getattr(User, field) == value)
        elif field == "username_contains":
            filter_conditions.append(User.username.ilike(f"%{value}%"))
        elif field.endswith("_in"):
            column = getattr(User, field[:-3]) 
            if isinstance(value, list):
                filter_conditions.filter(column.in_(value))
            else:
                # Handle single value case
                filter_conditions.append(column == value)


    if filter_conditions:
        query = query.filter(or_(*filter_conditions))

    res = query.all()
    return [UserData(**user_to_dict(user)) for user in res]



async def get_user_friends(db: Session, user_id: str):
    user: User = db.query(User).filter(User.user_id == user_id).first()
    return user.friends


async def update_user(db: Session, user_id: int, **kwargs) -> None:
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
        if hasattr(User, field):  # Check if the field exists in the User model
            print(field, value)
            setattr(user, field, value)
        else:
            raise ValueError(f"User object does not have attribute {field}")

    db.commit()
    return user


async def filter_users(db: Session, skip: int = 0, limit: int = 100, **filters):
    query = db.query(User).offset(skip).limit(limit)

    filter_conditions = []

    for field, value in filters.items():
        if hasattr(User, field):
            filter_conditions.append(getattr(User, field) == value)
        elif field == "username_contains":
            filter_conditions.append(User.username.ilike(f"%{value}%"))
        elif field.endswith("_in"):
            column_name = field[:-3]  # Removing the "_in" suffix
            filter_conditions.append(getattr(User, column_name).any(value))

    if filter_conditions:
        query = query.filter(or_(*filter_conditions))

    return query.all()

