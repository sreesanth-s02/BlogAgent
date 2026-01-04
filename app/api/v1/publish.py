from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.auth import get_current_user
from app.database.db import get_db
from app.blogger.service import publish_post
from app.blogger.html_builder import build_html
from app.api.rate_limit import rate_limit
import requests

router = APIRouter()


class PublishRequest(BaseModel):
    blog_id: int


def validate_image(url: str) -> bool:
    try:
        r = requests.head(url, timeout=5)
        return r.status_code == 200 and "image" in r.headers.get("Content-Type", "")
    except Exception:
        return False


@router.post(
    "/publish",
    dependencies=[Depends(rate_limit("publish", 3, 60))]
)
def publish_blog(payload: PublishRequest, user=Depends(get_current_user)):
    db = get_db()
    cur = db.cursor()

    # Fetch blog
    cur.execute("SELECT * FROM blogs WHERE id=?", (payload.blog_id,))
    blog = cur.fetchone()
    if not blog:
        raise HTTPException(404, "Blog not found")

    if blog["status"] == "published":
        raise HTTPException(400, "Blog already published")

    if not user.get("blogger_token"):
        raise HTTPException(403, "Blogger not connected")

    # Fetch paragraphs
    cur.execute("""
        SELECT content FROM blog_paragraphs
        WHERE blog_id=?
        ORDER BY paragraph_index
    """, (payload.blog_id,))
    paragraphs = [r["content"] for r in cur.fetchall()]

    # Validate image
    if blog["image_url"] and not validate_image(blog["image_url"]):
        raise HTTPException(400, "Invalid image URL")

    html = build_html(
        title=blog["main_heading"],
        paragraphs=paragraphs,
        image_url=blog["image_url"],
        position=blog["image_position"],
    )

    new_token, url = publish_post(
        token=user["blogger_token"],
        refresh_token=user["blogger_refresh_token"],
        blog_id=user["blogger_blog_id"],
        title=blog["main_heading"],
        html=html,
    )

    # Save new access token + publish state
    cur.execute("""
        UPDATE users
        SET blogger_token=?
        WHERE id=?
    """, (new_token, user["id"]))

    cur.execute("""
        UPDATE blogs
        SET is_published=1, published_url=?
        WHERE id=?
    """, (url, payload.blog_id))

    db.commit()

    return {
        "status": "published",
        "url": url
    }
