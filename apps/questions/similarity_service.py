import math


SIMILARITY_THRESHOLD = 0.70


def cosine_similarity(vector_a, vector_b):
    """Calculate cosine similarity between two vectors."""

    if not vector_a or not vector_b:
        return 0.0

    if len(vector_a) != len(vector_b):
        return 0.0

    dot_product = sum(
        a * b for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(
        sum(a * a for a in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(b * b for b in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def find_similar_questions(
    new_embedding,
    questions,
    threshold=SIMILARITY_THRESHOLD,
    limit=5,
):
    """Find the most similar existing questions."""

    matches = []

    for question in questions:

        if not question.embedding:
            continue

        similarity = cosine_similarity(
            new_embedding,
            question.embedding
        )

        if similarity >= threshold:

            matches.append({
                "id": question.id,
                "question_text": question.question_text,
                "similarity": round(
                    similarity * 100,
                    2
                ),
            })

    matches.sort(
        key=lambda item: item["similarity"],
        reverse=True
    )

    return matches[:limit]