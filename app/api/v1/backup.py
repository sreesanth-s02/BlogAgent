from fastapi import APIRouter, Depends
from app.core.jwt_utils import jwt_required
from app.database.db import get_db
from app.api.rate_limit import rate_limit

router = APIRouter()

@router.get(
    "/backup",
    dependencies=[
        Depends(jwt_required),
        Depends(rate_limit("backup", 2, 300))
    ]
)
def backup_db():
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT * FROM blogs")
    blogs = [dict(r) for r in cur.fetchall()]

    cur.execute("SELECT * FROM blog_paragraphs")
    paragraphs = [dict(r) for r in cur.fetchall()]

    return {
        "blogs": blogs,
        "paragraphs": paragraphs
    }
