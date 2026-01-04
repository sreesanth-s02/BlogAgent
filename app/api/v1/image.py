from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from app.core.auth import get_current_user
from app.llm.groq_client import groq_chat
from app.llm.prompts import IMAGE_KEYWORD_PROMPT
from app.api.rate_limit import rate_limit
from app.database.db import get_db
from app.services.image_search import search_unsplash
import requests

router = APIRouter()

# ----------------------------
# IMAGE KEYWORD GENERATION
# ----------------------------
class ImageKeywordRequest(BaseModel):
    blog_title: str
    blog_summary: str


@router.post(
    "/image/keywords",
    dependencies=[
        Depends(get_current_user),
        Depends(rate_limit("image_keywords", 5, 60))
    ]
)
def generate_image_keywords(payload: ImageKeywordRequest):
    keywords = groq_chat(
        system_prompt=IMAGE_KEYWORD_PROMPT,
        user_prompt=f"""
Title: {payload.blog_title}
Summary: {payload.blog_summary}
"""
    )

    cleaned = [
    k.strip()
    for k in keywords.split(",")
    if 2 < len(k.strip()) < 40
    ]

    return {"keywords": cleaned[:8]}



# ----------------------------
# IMAGE SEARCH (UNSPLASH)
# ----------------------------
@router.get(
    "/image/search",
    dependencies=[
        Depends(get_current_user),
        Depends(rate_limit("image_search", 10, 60))
    ]
)
def search_images(q: str = Query(..., min_length=3)):
    return {"results": search_unsplash(q)}


# ----------------------------
# IMAGE SELECT FOR BLOG
# ----------------------------
class ImageSelectRequest(BaseModel):
    blog_id: int
    image_url: str
    position: str = "top"  # top | bottom


def validate_image(url: str) -> bool:
    try:
        r = requests.head(url, timeout=5)
        return r.status_code == 200 and "image" in r.headers.get("Content-Type", "")
    except Exception:
        return False


@router.post(
    "/image/select",
    dependencies=[
        Depends(get_current_user),
        Depends(rate_limit("image_select", 10, 60))
    ]
)
def select_image(payload: ImageSelectRequest):
    if payload.position not in ("top", "bottom"):
        raise HTTPException(400, "Invalid image position")

    if not validate_image(payload.image_url):
        raise HTTPException(400, "Invalid image URL")

    db = get_db()
    cur = db.cursor()

    cur.execute("""
        UPDATE blogs
        SET image_url=?, image_position=?
        WHERE id=? AND status!='published'
    """, (
        payload.image_url,
        payload.position,
        payload.blog_id
    ))

    db.commit()

    if cur.rowcount == 0:
        raise HTTPException(
            400,
            "Cannot attach image to published or missing blog"
        )

    return {"status": "image_attached"}
