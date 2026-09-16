from .question_generation_service import generate_question
from .question_validation_service import validate_generated_question
from .question_generation_similarity_service import (
    check_generated_question_against_bank,
)


# =========================================================
# CONFIGURATION
# =========================================================

DEFAULT_MAX_ATTEMPTS = 3

# A question with similarity >= 90% is a duplicate.
DUPLICATE_THRESHOLD = 90.0


# =========================================================
# GENERATE + VALIDATE + DUPLICATE CHECK
# =========================================================

def generate_valid_unique_question(
    subject,
    unit,
    marks,
    bloom_level,
    difficulty,
    question_type,
    teacher=None,
    max_attempts=DEFAULT_MAX_ATTEMPTS,
):
    """
    Generate a question and keep regenerating until:

    1. The question passes AI validation.
    2. The question is not a duplicate.

    Nothing is saved to the database.

    Returns the final accepted question or a failure result.
    """

    try:
        max_attempts = int(max_attempts)
    except (TypeError, ValueError):
        max_attempts = DEFAULT_MAX_ATTEMPTS

    if max_attempts < 1:
        max_attempts = DEFAULT_MAX_ATTEMPTS

    attempts = []

    for attempt_number in range(1, max_attempts + 1):

        # =================================================
        # STEP 1 — GENERATE
        # =================================================

        try:

            generated = generate_question(
                subject=subject,
                unit=unit,
                marks=marks,
                bloom_level=bloom_level,
                difficulty=difficulty,
                question_type=question_type,
            )

        except Exception as exc:

            attempts.append({
                "attempt": attempt_number,
                "status": "generation_failed",
                "error": str(exc),
            })

            continue

        question_text = generated[
            "question_text"
        ]

        # =================================================
        # STEP 2 — VALIDATE
        # =================================================

        try:

            validation = validate_generated_question(
                question_text=question_text,
                subject=subject,
                unit=unit,
                marks=marks,
                bloom_level=bloom_level,
                difficulty=difficulty,
                question_type=question_type,
            )

        except Exception as exc:

            attempts.append({
                "attempt": attempt_number,
                "question_text": question_text,
                "status": "validation_failed",
                "error": str(exc),
            })

            continue

        # -------------------------------------------------
        # Validation failed
        # -------------------------------------------------

        if not validation["valid"]:

            attempts.append({
                "attempt": attempt_number,
                "question_text": question_text,
                "status": "invalid",
                "validation": validation,
            })

            continue

        # =================================================
        # STEP 3 — DUPLICATE / SIMILARITY CHECK
        # =================================================

        try:

            similarity_result = (
                check_generated_question_against_bank(
                    question_text=question_text,
                    teacher=teacher,
                    subject=(
                        generated.get("subject")
                        if subject is None
                        else subject
                    ),
                    unit=unit,
                    marks=marks,
                    difficulty=difficulty,
                    bloom_level=bloom_level,
                    question_type=question_type,
                )
            )

        except Exception as exc:

            attempts.append({
                "attempt": attempt_number,
                "question_text": question_text,
                "status": "similarity_check_failed",
                "error": str(exc),
            })

            continue

        # -------------------------------------------------
        # Duplicate found
        # -------------------------------------------------

        if similarity_result["is_duplicate"]:

            attempts.append({
                "attempt": attempt_number,
                "question_text": question_text,
                "status": "duplicate",
                "similarity": similarity_result,
            })

            continue

        # =================================================
        # QUESTION PASSED
        # =================================================

        return {
            "success": True,

            "question_text": question_text,

            "subject": generated["subject"],
            "unit": generated["unit"],
            "marks": generated["marks"],
            "bloom_level": generated["bloom_level"],
            "difficulty": generated["difficulty"],
            "question_type": generated["question_type"],

            "model": generated.get("model"),

            "validation": validation,

            "similarity": similarity_result,

            "attempts_used": attempt_number,

            "attempt_history": attempts,
        }

    # =====================================================
    # ALL ATTEMPTS FAILED
    # =====================================================

    return {
        "success": False,

        "message": (
            f"Unable to generate a valid unique question "
            f"after {max_attempts} attempts."
        ),

        "attempts_used": max_attempts,

        "attempt_history": attempts,
    }