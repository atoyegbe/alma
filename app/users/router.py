from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from app.db.user import get_users
from app.db.user import get_user

router = APIRouter()


@router.get("/users", response_model=List[UserData], dependencies=[Depends(requires_auth)])
async def get_all_users(db: Session = Depends(get_db)):
    # todo : ability to filter users by genres
    try:
        return await get_users(db)
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")

# todo: update user profile
@router.post("/me")
async def update_user_profile():
    pass

# todo: user public profile data
@router.get("{user_id}", response_model=UserSchema)
async def get_user_data(user_id: str, db: Session = Depends(get_db)):
    try:
        return await get_user(db, user_id)
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")


@router.get("/me", response_model=UserSchema)
async def get_user_data(
    db: Session = Depends(get_db),
    current_user=Annotated[UserSchema, Depends(requires_auth)],
):
    try:
        user = await get_user(db, current_user.user_id)
        return UserSchema(*user)
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")


# todo: get recommended users based on music taste
@router.get("/me/recommendations")
async def get_user_recommendations(
    db: Session = Depends(get_db),
    current_user=Annotated[UserSchema, Depends(requires_auth)],
):
    pass


