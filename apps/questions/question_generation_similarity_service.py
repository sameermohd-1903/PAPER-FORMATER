from .embedding_service import generate_embedding
from .similarity_service import (
    cosine_similarity,
    DUPLICATE_THRESHOLD,
    SIMILARITY_THRESHOLD,
)


# =========================================================
# CHECK GENERATED QUESTION AGAINST QUESTION BANK
# =========================================================

def check_question_similarity(
    question_text,
    questions,
    limit=5,
):
    """
    Generate an embedding for the new question and compare it
    against existing questions.

    Returns duplicate/similar matches sorted by similarity.
    """

    question_text = str(
        question_text or ""
    ).strip()

    if not question_text:
        raise ValueError(
            "Question text cannot be empty."
        )

    # -----------------------------------------------------
    # Generate embedding for AI-generated question
    # -----------------------------------------------------

    new_embedding = generate_embedding(
        question_text
    )

    matches = []

    for question in questions:

        existing_embedding = getattr(
            question,
            "embedding",
            None,
        )

        # Existing question has no embedding.
        # It cannot participate in similarity checking.
        if not existing_embedding:
            continue

        similarity = cosine_similarity(
            new_embedding,
            existing_embedding,
        )

        # Only keep questions that are at least
        # the similarity threshold.
        if similarity < SIMILARITY_THRESHOLD:
            continue

        percentage = round(
            similarity * 100,
            2,
        )

        if similarity >= DUPLICATE_THRESHOLD:

            status = "duplicate"

        elif similarity >= 0.80:

            status = "highly_similar"

        else:

            status = "similar"

        matches.append({
            "id": question.id,
            "question_text": question.question_text,
            "similarity": percentage,
            "similarity_score": round(
                similarity,
                4,
            ),
            "status": status,
        })

    # Highest similarity first
    matches.sort(
        key=lambda item: (
            item["similarity"],
            -item["id"],
        ),
        reverse=True,
    )

    return {
        "is_duplicate": any(
            item["status"] == "duplicate"
            for item in matches
        ),

        "has_similar": bool(matches),

        "matches": matches[:limit],

        "embedding": new_embedding,
    }


# =========================================================
# CHECK USING DJANGO QUESTION QUERYSET
# =========================================================

def check_generated_question_against_bank(
    question_text,
    teacher=None,
    subject=None,
    unit=None,
    marks=None,
    difficulty=None,
    bloom_level=None,
    question_type=None,
    limit=5,
):
    """
    Check an AI-generated question against the existing
    Question database.

    Optional filters allow us to compare the generated
    question only against relevant questions.
    """

    from .models import Question

    questions = Question.objects.filter(
        is_active=True,
    )

    # -----------------------------------------------------
    # Teacher filter
    # -----------------------------------------------------

    if teacher is not None:

        questions = questions.filter(
            teacher=teacher
        )

    # -----------------------------------------------------
    # Subject filter
    # -----------------------------------------------------

    if subject is not None:
    
        # Django Subject ForeignKey requires a Subject
        # object or numeric primary-key value.
        #
        # The generation service may provide the subject
        # as plain text such as "DBMS", so only apply this
        # filter when we actually receive a Subject object
        # or numeric ID.

        from django.db.models import Model

        if isinstance(subject, Model):

            questions = questions.filter(
                subject=subject
            )

        elif isinstance(subject, int):

            questions = questions.filter(
                subject_id=subject
            )

    # -----------------------------------------------------
    # Unit filter
    # -----------------------------------------------------

    if unit:

        questions = questions.filter(
            unit=str(unit)
        )

    # -----------------------------------------------------
    # Marks filter
    # -----------------------------------------------------

    if marks is not None:

        questions = questions.filter(
            marks=int(marks)
        )

    # -----------------------------------------------------
    # Difficulty filter
    # -----------------------------------------------------

    if difficulty:

        questions = questions.filter(
            difficulty=str(
                difficulty
            ).strip().lower()
        )

    # -----------------------------------------------------
    # Bloom filter
    # -----------------------------------------------------

    if bloom_level:

        questions = questions.filter(
            bloom_level=str(
                bloom_level
            ).strip()
        )

    # -----------------------------------------------------
    # Question type filter
    # -----------------------------------------------------

    if question_type:

        question_type = str(
            question_type
        ).strip().lower()

        if question_type == "cs":
            question_type = "casestudy"

        questions = questions.filter(
            question_type=question_type
        )

    return check_question_similarity(
        question_text=question_text,
        questions=questions,
        limit=limit,
    )


# =========================================================
# FINAL DUPLICATE DECISION
# =========================================================

def validate_question_uniqueness(
    question_text,
    questions,
):
    """
    Determine whether an AI-generated question can be
    considered unique.

    Returns:
        unique = True
            No duplicate >= 90%

        unique = False
            Duplicate >= 90%
    """

    result = check_question_similarity(
        question_text=question_text,
        questions=questions,
    )

    return {
        "unique": not result["is_duplicate"],
        "is_duplicate": result["is_duplicate"],
        "has_similar": result["has_similar"],
        "matches": result["matches"],
        "embedding": result["embedding"],
    }