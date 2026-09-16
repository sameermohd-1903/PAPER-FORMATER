from apps.questions.similarity_service import cosine_similarity


# =========================================================
# RANKING WEIGHTS
# =========================================================

BLOOM_MATCH_SCORE = 40
TYPE_MATCH_SCORE = 20
SIMILARITY_WEIGHT = 40


# =========================================================
# NORMALIZE VALUES
# =========================================================

def normalize(value):
    return str(value or "").strip().lower()


# =========================================================
# GET QUESTION TYPE
# =========================================================

def get_question_type(question):

    return normalize(
        getattr(question, "question_type", "")
    )


# =========================================================
# GET BLOOM LEVEL
# =========================================================

def get_bloom_level(question):

    return normalize(
        getattr(question, "bloom_level", "")
    )


# =========================================================
# CALCULATE SEMANTIC SIMILARITY
# =========================================================

def calculate_similarity(
    reference_question=None,
    candidate_question=None,
    reference_embedding=None,
):
    """
    Calculate semantic similarity between a reference
    and a candidate question.

    Two reference methods are supported:

    1. reference_question
       Used by Smart Replace.

    2. reference_embedding
       Used by AI-assisted automatic paper generation.

    The candidate must have an embedding.
    """

    # ---------------------------------------------------------
    # Get candidate embedding
    # ---------------------------------------------------------

    if not candidate_question:

        return 0.0

    candidate_embedding = getattr(
        candidate_question,
        "embedding",
        None
    )

    if not candidate_embedding:

        return 0.0


    # ---------------------------------------------------------
    # Get reference embedding
    # ---------------------------------------------------------

    if reference_embedding:

        source_embedding = reference_embedding

    elif reference_question:

        source_embedding = getattr(
            reference_question,
            "embedding",
            None
        )

    else:

        return 0.0


    # ---------------------------------------------------------
    # Validate reference embedding
    # ---------------------------------------------------------

    if not source_embedding:

        return 0.0


    # ---------------------------------------------------------
    # Calculate cosine similarity
    # ---------------------------------------------------------

    return cosine_similarity(
        source_embedding,
        candidate_embedding
    )


# =========================================================
# SCORE ONE QUESTION
# =========================================================

def score_question(
    question,
    required_bloom_level=None,
    required_question_type=None,
    reference_question=None,
    reference_embedding=None,
):
    """
    Calculate a ranking score.

    IMPORTANT:
    This function does NOT apply hard constraints.

    Hard constraints must already be applied by Django.

    Ranking:

        Bloom match          = 40 points
        Question type match  = 20 points
        Semantic similarity  = 40 points

        Maximum score        = 100
    """

    score = 0.0


    # =====================================================
    # BLOOM MATCH
    # =====================================================

    bloom_match = False

    if required_bloom_level:

        bloom_match = (
            get_bloom_level(question)
            ==
            normalize(required_bloom_level)
        )

        if bloom_match:

            score += BLOOM_MATCH_SCORE


    # =====================================================
    # QUESTION TYPE MATCH
    # =====================================================

    type_match = False

    if required_question_type:

        question_type = get_question_type(
            question
        )

        required_type = normalize(
            required_question_type
        )


        # -------------------------------------------------
        # Handle legacy "cs"
        # -------------------------------------------------

        if question_type == "cs":

            question_type = "casestudy"


        if required_type == "cs":

            required_type = "casestudy"


        type_match = (
            question_type == required_type
        )


        if type_match:

            score += TYPE_MATCH_SCORE


    # =====================================================
    # SEMANTIC SIMILARITY
    # =====================================================

    similarity = calculate_similarity(
        reference_question=reference_question,
        candidate_question=question,
        reference_embedding=reference_embedding,
    )


    # Convert similarity to ranking points

    similarity_score = (
        similarity
        * SIMILARITY_WEIGHT
    )


    score += similarity_score


    # =====================================================
    # RETURN RESULT
    # =====================================================

    return {

        "question": question,

        "score": round(
            score,
            4
        ),

        "similarity": round(
            similarity,
            4
        ),

        "similarity_score": round(
            similarity_score,
            4
        ),

        "bloom_match": bloom_match,

        "type_match": type_match,

    }


# =========================================================
# RANK QUESTIONS
# =========================================================

def rank_questions(
    questions,
    required_bloom_level=None,
    required_question_type=None,
    reference_question=None,
    reference_embedding=None,
):
    questions = list(questions)

    if not questions:
        return []

    ranked = []

    for question in questions:

        ranked.append(
            score_question(
                question=question,
                required_bloom_level=required_bloom_level,
                required_question_type=required_question_type,
                reference_question=reference_question,
                reference_embedding=reference_embedding,
            )
        )

    # =========================================================
    # CHECK WHETHER EXACT BLOOM + TYPE MATCHES EXIST
    # =========================================================

    exact_matches = [
        item
        for item in ranked
        if (
            item["bloom_match"]
            and item["type_match"]
        )
    ]

    # =========================================================
    # IF EXACT MATCHES EXIST
    # RANK ONLY THOSE QUESTIONS
    # =========================================================

    if exact_matches:

        ranked = exact_matches

    else:

        # -----------------------------------------------------
        # If no exact Bloom + Type match exists,
        # keep all candidates and rank them by:
        #
        # 1. Bloom match
        # 2. Type match
        # 3. Semantic similarity
        # -----------------------------------------------------

        ranked.sort(
            key=lambda item: (
                item["bloom_match"],
                item["type_match"],
                item["similarity"],
                -item["question"].id,
            ),
            reverse=True
        )

        return ranked

    # =========================================================
    # RANK EXACT MATCHES BY SEMANTIC SIMILARITY
    # =========================================================

    ranked.sort(
        key=lambda item: (
            item["similarity"],
            -item["question"].id,
        ),
        reverse=True
    )

    return ranked


# =========================================================
# SELECT BEST QUESTION
# =========================================================

def select_best_question(
    questions,
    required_bloom_level=None,
    required_question_type=None,
    reference_question=None,
    reference_embedding=None,
):
    """
    Return the highest-ranked question.

    Returns:

        {
            "question": Question,
            "score": float,
            "similarity": float,
            "similarity_score": float,
            "bloom_match": bool,
            "type_match": bool,
        }

    or None when no candidates exist.
    """

    ranked = rank_questions(

        questions=questions,

        required_bloom_level=
            required_bloom_level,

        required_question_type=
            required_question_type,

        reference_question=
            reference_question,

        reference_embedding=
            reference_embedding,

    )


    if not ranked:

        return None


    return ranked[0]