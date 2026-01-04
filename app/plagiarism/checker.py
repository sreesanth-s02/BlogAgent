from difflib import SequenceMatcher
import uuid

SIMILARITY_THRESHOLD = 0.75


def similarity_score(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def sentence_level_plagiarism(text: str, references: list[str]) -> list[dict]:
    """
    Splits paragraph into sentences and checks each one.
    """
    sentences = [
        s.strip()
        for s in text.replace("\n", " ").split(".")
        if len(s.strip()) > 15
    ]

    results = []

    for sentence in sentences:
        max_score = 0.0
        for ref in references:
            max_score = max(max_score, similarity_score(sentence, ref))

        results.append({
            "id": str(uuid.uuid4()),
            "text": sentence,
            "similarity": round(max_score, 2),
            "flagged": max_score >= SIMILARITY_THRESHOLD
        })

    return results
