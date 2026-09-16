import math


# ---------------------------------------
# Similarity Thresholds
# ---------------------------------------

DUPLICATE_THRESHOLD = 0.90
SIMILARITY_THRESHOLD = 0.70


# ---------------------------------------
# Cosine Similarity
# ---------------------------------------

def cosine_similarity(vector_a, vector_b):

    if not vector_a or not vector_b:
        return 0.0

    if len(vector_a) != len(vector_b):
        return 0.0

    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(
        sum(a * a for a in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(b * b for b in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (
        magnitude_a * magnitude_b
    )


# ---------------------------------------
# Find Similar Questions
# ---------------------------------------

def find_similar_questions(
    new_embedding,
    questions,
    threshold=SIMILARITY_THRESHOLD,
    limit=5
):

    matches = []

    for question in questions:

        if not question.embedding:
            continue

        similarity = cosine_similarity(
            new_embedding,
            question.embedding
        )

        if similarity >= threshold:

            percentage = round(
                similarity * 100,
                2
            )

            if similarity >= DUPLICATE_THRESHOLD:
                status = "duplicate"
            elif similarity >= 0.80:
                status = "highly_similar"
            else:
                status = "similar"

            matches.append({

                "id": question.id,

                "question_text":
                    question.question_text,

                "similarity":
                    percentage,

                "status":
                    status,
            })

    matches.sort(
        key=lambda item: item["similarity"],
        reverse=True
    )

    return matches[:limit]