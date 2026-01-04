from fastapi import APIRouter, Depends, HTTPException
from app.core.jwt_utils import jwt_required, create_access_token
from app.database.db import get_db
from app.api.rate_limit import rate_limit

router = APIRouter()

# ----------------------------
# GET SINGLE BLOG
# ----------------------------
@router.get(
    "/blog/{blog_id}",
    dependencies=[
        Depends(jwt_required),
        Depends(rate_limit("get_blog", 30, 60))
    ]
)
def get_blog(blog_id: int):
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT * FROM blogs WHERE id=?", (blog_id,))
    blog = cur.fetchone()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    cur.execute("""
        SELECT id, content, similarity_score, status
        FROM blog_paragraphs
        WHERE blog_id=?
        ORDER BY paragraph_index
    """, (blog_id,))
    paragraphs = cur.fetchall()

    return {
        "id": blog["id"],
        "main_heading": blog["main_heading"],
        "overall_similarity": blog["overall_similarity"],
        "is_pinned": blog["is_pinned"],
        "is_archived": blog["is_archived"],
        "is_published": blog["status"] == "published",
        "paragraphs": [
            {
                "id": p["id"],
                "text": p["content"],
                "similarity": p["similarity_score"],
                "risk": p["status"]
            }
            for p in paragraphs
        ]
    }


# ----------------------------
# DELETE BLOG
# ----------------------------
@router.delete(
    "/blog/{blog_id}",
    dependencies=[
        Depends(jwt_required),
        Depends(rate_limit("delete_blog", 10, 60))
    ]
)
def delete_blog(blog_id: int):
    db = get_db()
    cur = db.cursor()

    # delete child paragraphs first
    cur.execute("DELETE FROM blog_paragraphs WHERE blog_id=?", (blog_id,))

    # then delete blog
    cur.execute("DELETE FROM blogs WHERE id=?", (blog_id,))
    db.commit()

    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Blog not found")

    return {"status": "deleted"}


# ----------------------------
# PIN / UNPIN BLOG
# ----------------------------
@router.post(
    "/blog/{blog_id}/pin",
    dependencies=[
        Depends(jwt_required),
        Depends(rate_limit("pin_blog", 10, 60))
    ]
)
def toggle_pin(blog_id: int):
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT is_pinned FROM blogs WHERE id=?", (blog_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Blog not found")

    new_state = 0 if row["is_pinned"] else 1

    cur.execute(
        "UPDATE blogs SET is_pinned=? WHERE id=?",
        (new_state, blog_id)
    )
    db.commit()

    return {"pinned": bool(new_state)}

# ----------------------------
# LIST BLOGS (WITH ARCHIVE FILTER)
# ----------------------------
from fastapi import Request

@router.get(
    "/blogs",
    dependencies=[
        Depends(jwt_required),
        Depends(rate_limit("blogs_list", 20, 60))
    ]
)
def list_blogs(request: Request):
    archived = request.query_params.get("archived", "false") == "true"

    cur = get_db().cursor()
    cur.execute("""
        SELECT id, content_name, is_pinned
        FROM blogs
        WHERE is_archived=?
        ORDER BY is_pinned DESC, created_at DESC
    """, (1 if archived else 0,))

    return [dict(r) for r in cur.fetchall()]

# ----------------------------
# SHARE BLOG (READ-ONLY)
# ----------------------------
@router.post(
    "/blog/{blog_id}/share",
    dependencies=[
        Depends(jwt_required),
        Depends(rate_limit("share_blog", 5, 60))
    ]
)
def share_blog(blog_id: int):
    cur = get_db().cursor()
    cur.execute("SELECT id FROM blogs WHERE id=?", (blog_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Blog not found")

    token = create_access_token(
        data={"blog_id": blog_id, "scope": "read"},
        expires_minutes=60 * 24
    )

    return {
        "share_url": f"/ui/shared.html?token={token}"
    }
#----------------------------
# EDIT NAME OF BLOG
#----------------------------
@router.put(
    "/blog/{blog_id}/rename",
    dependencies=[
        Depends(jwt_required),
        Depends(rate_limit("rename_blog", 10, 60))
    ]
)
def rename_blog(blog_id: int, payload: dict):
    new_name = payload.get("content_name")
    if not new_name:
        raise HTTPException(400, "content_name required")

    db = get_db()
    cur = db.cursor()

    cur.execute("""
        UPDATE blogs
        SET content_name=?
        WHERE id=? AND status != 'published'
    """, (new_name, blog_id))

    db.commit()

    if cur.rowcount == 0:
        raise HTTPException(
            400,
            "Cannot rename published or missing blog"
        )

    return {"status": "renamed", "content_name": new_name}
# ----------------------------
# EXPORT BLOG
# ----------------------------
@router.get(
    "/blog/{blog_id}/export",
    dependencies=[Depends(jwt_required)]
)
def export_blog(blog_id: int, format: str = "md"):
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT main_heading FROM blogs WHERE id=?", (blog_id,))
    blog = cur.fetchone()
    if not blog:
        raise HTTPException(404)

    cur.execute("""
        SELECT content FROM blog_paragraphs
        WHERE blog_id=?
        ORDER BY paragraph_index
    """, (blog_id,))
    paragraphs = [r["content"] for r in cur.fetchall()]

    if format == "md":
        content = f"# {blog['main_heading']}\n\n"
        content += "\n\n".join(paragraphs)
        return {"format": "markdown", "content": content}

    if format == "html":
        html = f"<h1>{blog['main_heading']}</h1>"
        for p in paragraphs:
            html += f"<p>{p}</p>"
        return {"format": "html", "content": html}

    raise HTTPException(400, "Unsupported format")
