

async def requires_auth(auth_token: Optional[str] = Header(None)) -> UserSchema:
    """
    Validate user
    """
    if not auth_token:
        raise HTTPException(status_code=401, detail="No auth header")

    if not auth_token.startswith("Bearer"):
        raise HTTPException(status_code=401, detail="'Bearer' prefix missing")

    token = auth_token[7:]
    if not token:
        raise HTTPException(status_code=401, detail="No token in auth header")

    db = SessionLocal()
    current_user = await get_user_by_token(db, token)
    if not current_user:
        raise HTTPException(status_code=401, detail="Unable to authenticate user")
    return current_user


def get_header(token: str):
    return {"Authorization": f"Bearer {token}"}
