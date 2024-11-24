
from fastapi import APIRouter
from fastapi import Request
from fastapi import Depends

from .datamodels import SimilarityPercentage
from .similarity import get_users_similiraity

from app.database.database import get_db
from app.users import get_user

router = APIRouter()

@router.get("/similarity-score", response_model=SimilarityPercentage)
async def check_match(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Annotated[UserSchema, Depends(requires_auth)],
):
    match_id = request.query_params["match_id"]
    match_user = await get_user(db, match_id)
    if not match_user:
        return {"message": "users does not exist"}

    similarity_score = get_users_similiraity(current_user, match_user)

    # converting cosine similarity score to percentage
    similarity_score = (
        0.0 if similarity_score == 0.0 else (similarity_score + 1) / 2 * 100
    )

    return SimilarityPercentage(similarity_score)

