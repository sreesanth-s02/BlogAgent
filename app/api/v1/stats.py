from fastapi import APIRouter, Depends
from app.core.jwt_utils import jwt_required
from app.database.db import get_db
from app.api.rate_limit import rate_limit

router = APIRouter()

@router.get(
    "/stats",
    dependencies=[
        Depends(jwt_required),
        Depends(rate_limit("stats", 10, 60))
    ]
)
def get_stats():
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT COUNT(*) FROM blogs")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM blogs WHERE status='published'")
    published = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM blogs WHERE status!='published'")
    drafts = cur.fetchone()[0]

    cur.execute("SELECT AVG(overall_similarity) FROM blogs")
    avg_similarity = cur.fetchone()[0] or 0

    cur.execute("""
        SELECT MAX(published_at)
        FROM blogs
        WHERE status='published'
    """)
    last_published = cur.fetchone()[0]

    return {
        "total_blogs": total,
        "published": published,
        "drafts": drafts,
        "average_similarity": round(avg_similarity, 2),
        "last_published": last_published
    }
