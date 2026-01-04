from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.auth import get_current_user
from app.llm.groq_client import groq_chat
from app.llm.prompts import REWRITE_SYSTEM_PROMPT
from app.database.db import get_db
from app.plagiarism.checker import sentence_level_plagiarism
from app.api.rate_limit import rate_limit
from pydantic import BaseModel,Field

router = APIRouter()


class RewriteRequest(BaseModel):
    blog_id: int
    paragraph_id: int
    sentence: str = Field(..., min_length=10, max_length=500)
    instruction: str = Field(..., min_length=5, max_length=300)



@router.post(
    "/rewrite",
    dependencies=[Depends(rate_limit("rewrite", 10, 60))]
)
def rewrite_sentence(payload: RewriteRequest, user=Depends(get_current_user)):
    db = get_db()
    cur = db.cursor()

    # 🚫 Prevent rewrite on published blogs
    cur.execute(
    "SELECT status FROM blogs WHERE id=?",
    (payload.blog_id,)
    )   
    blog_row = cur.fetchone()
    if not blog_row:
        raise HTTPException(404, "Blog not found")

    if blog_row["status"] == "published":
        raise HTTPException(400, "Published blogs cannot be edited")

    # Fetch paragraph
    cur.execute("""
        SELECT content
        FROM blog_paragraphs
        WHERE id=? AND blog_id=?
    """, (payload.paragraph_id, payload.blog_id))
    para_row = cur.fetchone()

    if not para_row:
        raise HTTPException(404, "Paragraph not found")

    old_content = para_row["content"]

    # Rewrite sentence via LLM
    rewritten_sentence = groq_chat(
        system_prompt=REWRITE_SYSTEM_PROMPT,
        user_prompt=f"""
Original sentence:
{payload.sentence}

Instruction:
{payload.instruction}
"""
    )

    if not rewritten_sentence:
        raise HTTPException(500, "Rewrite failed")

    # Replace sentence in paragraph
    if payload.sentence not in old_content:
        raise HTTPException(400, "Sentence not found in paragraph")

    new_content = old_content.replace(
        payload.sentence,
        rewritten_sentence.strip(),
        1
    )

    # Re-run plagiarism on updated paragraph
    plagiarism = sentence_level_plagiarism(new_content, [])

    max_similarity = max(
        [s["similarity"] for s in plagiarism],
        default=0
    )

    status = "rewrite_required" if max_similarity >= 0.75 else "safe"

    # Update paragraph
    cur.execute("""
        UPDATE blog_paragraphs
        SET content=?, similarity_score=?, status=?
        WHERE id=?
    """, (
        new_content,
        max_similarity,
        status,
        payload.paragraph_id
    ))

    # Update overall blog similarity
    cur.execute("""
        UPDATE blogs
        SET overall_similarity=(
            SELECT MAX(similarity_score)
            FROM blog_paragraphs
            WHERE blog_id=?
        )
        WHERE id=?
    """, (payload.blog_id, payload.blog_id))

    db.commit()

    return {
        "rewritten_sentence": rewritten_sentence.strip(),
        "paragraph_similarity": round(max_similarity, 2),
        "paragraph_status": status
    }
