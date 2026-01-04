from fastapi import Depends, HTTPException
from app.core.jwt_utils import jwt_required
from app.database.db import get_db


def get_current_user(payload=Depends(jwt_required)):
    """
    Extracts user from JWT payload.
    Assumes token contains user_id.
    """
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cur.fetchone()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return dict(user)
