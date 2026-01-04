from fastapi import APIRouter, HTTPException
from jose import JWTError, ExpiredSignatureError
from app.core.jwt_utils import decode_token
from app.database.db import get_db

router = APIRouter()

@router.get("/shared")
def view_shared_blog(token: str):
    try:
        payload = decode_token(token)
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="This shared link has expired"
        )
    except JWTError:
        raise HTTPException(
            status_code=403,
            detail="Invalid or tampered link"
        )

    if payload.get("scope") != "read":
        raise HTTPException(status_code=403, detail="Access denied")

    blog_id = payload.get("blog_id")

    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT main_heading FROM blogs WHERE id=?", (blog_id,))
    blog = cur.fetchone()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    cur.execute("""
        SELECT content
        FROM blog_paragraphs
        WHERE blog_id=?
        ORDER BY paragraph_index
    """, (blog_id,))

    return {
        "title": blog["main_heading"],
        "content": [r["content"] for r in cur.fetchall()],
        "read_only": True
    }
