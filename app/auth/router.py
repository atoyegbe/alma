from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse

from app.database.database import db_dependency
from app.auth.auth import get_current_user
from app.models.models import User
from app.auth import auth
from app.constant import TOKEN_URL, CLIENT_REDIRECT_URL
from app.users.users import create_user, get_user, update_user_profile
from datetime import datetime
import base64
import httpx


router = APIRouter()

@router.get("/callback")
async def spotify_login(request: Request, db: db_dependency):
    code_param = request.query_params.get("code")
    try:
        data = {
            "code": code_param,
            "redirect_uri": CLIENT_REDIRECT_URL,
            "grant_type": "authorization_code",
        }
        credentials = f"{client_id}:{client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {encoded_credentials}",
        }

        response = await app.state.http_client.post(
            TOKEN_URL, data=data, headers=headers
        )
        token_info = response.json()
        access_token = token_info["access_token"]

        user_data = await get_spotify_user_data(access_token)

        existing_user = await get_user(db, user_data["id"])
        if not existing_user:
            new_user = UserSchema(
                user_id=user_data["id"],
                username=user_data["display_name"],
                country=user_data["country"],
                auth_token=token_info["access_token"],
                refresh_token=token_info["refresh_token"],
                token_expires_date=datetime.now().timestamp()
                + token_info["expires_in"],
            )
            await create_user(db, new_user)

            await save_user_top_tracks(new_user.auth_token, db)
            await save_top_artists(new_user.auth_token, db)
            return JSONResponse(
                content={
                    "auth-token": new_user.auth_token,
                    "auth-refresh-token": new_user.refresh_token,
                },
                status_code=status.HTTP_200_OK,
            )
        return JSONResponse(
            content={
                "auth_token": existing_user.auth_token,
                "refresh_token": existing_user.refresh_token,
            },
            status_code=status.HTTP_200_OK,
        )

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")


@router.get("/refresh-token")
async def refresh_token(refresh_token: str, request: Request):
    if datetime.now().timestamp() > request.session["expires_at"]:
        req_body = {
            "grant_type": "refresh_token",
            "refresh_token": request.session["refresh_token"],
            "client_id": client_id,
            "client_secret": client_secret,
        }

        try:
            response = await app.state.http_client.post(TOKEN_URL, data=req_body)

            if response.status_code >= 400:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Callback error: {response.text}",
                )

            new_token_info = response.json()
            request.session["access_token"] = new_token_info["access_token"]
            request.session["expires_at"] = (
                datetime.now().timestamp() + new_token_info["expires_in"]
            )

            return RedirectResponse("/")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")


# TODO: : Handle proper logout
@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/")
