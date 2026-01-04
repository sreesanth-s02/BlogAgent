from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.auth import get_current_user
from app.llm.groq_client import groq_chat
from app.llm.prompts import BLOG_SYSTEM_PROMPT
from app.database.db import get_db
from app.plagiarism.checker import sentence_level_plagiarism
from app.api.rate_limit import rate_limit
from pydantic import BaseModel,Field

router = APIRouter()

class GenerateRequest(BaseModel):
    content_name: str = Field(..., min_length=3, max_length=120)
    topic: str = Field(..., min_length=20, max_length=500)



@router.post(
    "/generate",
    dependencies=[Depends(rate_limit("generate", 5, 60))]
)
def generate_blog(payload: GenerateRequest, user=Depends(get_current_user)):
    db = get_db()
    cur = db.cursor()

    blog_data = groq_chat(
        system_prompt=BLOG_SYSTEM_PROMPT,
        user_prompt=payload.topic
    )

    if not blog_data:
        raise HTTPException(500, "LLM generation failed")

    # Insert blog
    cur.execute("""
        INSERT INTO blogs (
            content_name,
            topic,
            main_heading,
            overall_similarity,
            status
        )
        VALUES (?, ?, ?, 0, 'draft')
    """, (
        payload.content_name,
        payload.topic,
        blog_data["title"]
    ))

    blog_id = cur.lastrowid

    similarities = []
    paragraph_index = 0

    for section in blog_data["sections"]:
        plagiarism = sentence_level_plagiarism(section["content"], [])

        max_similarity = max(
            (s["similarity"] for s in plagiarism),
            default=0
        )
        similarities.append(max_similarity)

        cur.execute("""
            INSERT INTO blog_paragraphs
            (blog_id, paragraph_index, content, similarity_score, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            blog_id,
            paragraph_index,
            section["content"],
            max_similarity,
            "rewrite_required" if max_similarity >= 0.75 else "safe"
        ))

        paragraph_index += 1

    overall_similarity = round(max(similarities), 2) if similarities else 0

    cur.execute("""
        UPDATE blogs SET overall_similarity=? WHERE id=?
    """, (overall_similarity, blog_id))

    db.commit()

    return {
        "blog_id": blog_id,
        "overall_similarity": overall_similarity
    }
