from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
import requests
from app.core.config import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI
)
from app.core.auth import get_current_user
from app.core.jwt_utils import create_access_token, decode_token
from app.database.db import get_db

router = APIRouter()


@router.get("/auth/blogger")
def blogger_auth(user=Depends(get_current_user)):
    """
    Step 1: Redirect to Google OAuth
    State is a SIGNED JWT
    """
    state = create_access_token(
        data={"user_id": user["id"], "scope": "oauth"},
        expires_minutes=10
    )

    url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        "&response_type=code"
        "&scope=https://www.googleapis.com/auth/blogger"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        "&access_type=offline&prompt=consent"
        f"&state={state}"
    )
    return RedirectResponse(url)


@router.get("/auth/blogger/callback")
def blogger_callback(code: str, state: str):
    """
    Step 2: Validate state JWT and exchange token
    """
    try:
        payload = decode_token(state)
    except Exception:
        raise HTTPException(403, "Invalid OAuth state")

    if payload.get("scope") != "oauth":
        raise HTTPException(403, "Invalid OAuth scope")

    user_id = payload["user_id"]

    token_res = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": GOOGLE_REDIRECT_URI,
        },
    )

    token_data = token_res.json()
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")

    if not access_token:
        raise HTTPException(400, "Failed to connect Blogger")

    db = get_db()
    cur = db.cursor()

    cur.execute("""
        UPDATE users
        SET blogger_token=?, blogger_refresh_token=?
        WHERE id=?
    """, (access_token, refresh_token, user_id))

    db.commit()

    return RedirectResponse("/ui/?blogger=connected")
