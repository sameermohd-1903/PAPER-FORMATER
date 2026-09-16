import json
import os
import requests
from django.conf import settings
from .similarity_service import cosine_similarity
from apps.questions.models import Question
from apps.questions.question_selection_service import rank_questions

# ============================================================
# CONFIGURATION
# ============================================================

OLLAMA_URL = os.environ.get(
    "OLLAMA_URL",
    "http://127.0.0.1:11434/api/generate"
)

OLLAMA_MODEL = os.environ.get(
    "OLLAMA_MODEL",
    "qwen3:8b"
)

# Similarity threshold for detecting repetitive questions
SIMILARITY_THRESHOLD = 0.70

# Strong duplicate threshold
DUPLICATE_THRESHOLD = 0.90


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _display_bloom(question):
    """
    Return Bloom level as:
    1 = Remember
    2 = Understand
    ...
    6 = Create
    """

    return str(question.bloom_level or "").strip()


def _display_difficulty(question):
    value = str(question.difficulty or "").strip().lower()

    mapping = {
        "easy": "Easy",
        "medium": "Medium",
        "hard": "Hard",
    }

    return mapping.get(value, value.title())


def _display_question_type(question):
    value = str(question.question_type or "").strip().lower()

    mapping = {
        "mcq": "MCQ",
        "ftq": "Following the Questions",
        "cs": "Case Study",
        "casestudy": "Case Study",
    }

    return mapping.get(value, value)


# ============================================================
# GET PAPER QUESTIONS
# ============================================================

def get_paper_questions(paper):
    """
    Get all questions belonging to a generated paper.

    GeneratedQuestion objects are returned with the related
    Question and PatternSection already loaded.
    """

    generated_questions = (
        paper.generated_questions
        .select_related(
            "question",
            "section",
        )
        .order_by("display_order")
    )

    return list(generated_questions)

# ============================================================
# GET PAPER QUESTIONS
# ============================================================

def calculate_basic_metrics(paper):
    """
    Calculate deterministic paper statistics.

    Important:
    A paper may display alternative questions.

    Example:
        Attempt Any 2 out of 3
        5 marks each

    Displayed marks:
        3 x 5 = 15

    Attemptable marks:
        2 x 5 = 10

    Therefore we keep both values separately.
    """

    generated_questions = get_paper_questions(paper)

    questions = [
        gq.question
        for gq in generated_questions
        if gq.question
    ]

    # ========================================================
    # DISPLAYED PAPER METRICS
    # ========================================================

    displayed_marks = sum(
        question.marks or 0
        for question in questions
    )

    displayed_question_count = len(questions)

    # ========================================================
    # UNIT DISTRIBUTION
    # ========================================================

    unit_distribution = {}

    for question in questions:

        unit = str(
            question.unit or "Unknown"
        ).strip()

        if unit not in unit_distribution:
            unit_distribution[unit] = 0

        unit_distribution[unit] += 1

    # ========================================================
    # BLOOM DISTRIBUTION
    # ========================================================

    bloom_distribution = {
        "1": 0,
        "2": 0,
        "3": 0,
        "4": 0,
        "5": 0,
        "6": 0,
    }

    for question in questions:

        bloom = _display_bloom(question)

        if bloom in bloom_distribution:
            bloom_distribution[bloom] += 1

    # ========================================================
    # DIFFICULTY DISTRIBUTION
    # ========================================================

    difficulty_distribution = {
        "easy": 0,
        "medium": 0,
        "hard": 0,
    }

    for question in questions:

        difficulty = str(
            question.difficulty or ""
        ).strip().lower()

        if difficulty in difficulty_distribution:
            difficulty_distribution[difficulty] += 1

    # ========================================================
    # QUESTION TYPE DISTRIBUTION
    # ========================================================

    question_type_distribution = {
        "mcq": 0,
        "ftq": 0,
        "casestudy": 0,
    }

    for question in questions:

        question_type = str(
            question.question_type or ""
        ).strip().lower()

        if question_type == "cs":
            question_type = "casestudy"

        if question_type in question_type_distribution:
            question_type_distribution[
                question_type
            ] += 1

    # ========================================================
    # PATTERN
    # ========================================================

    pattern = paper.pattern

    required_marks = (
        pattern.total_marks
        if pattern
        else None
    )

    # ========================================================
    # SECTION-WISE ATTEMPTABLE MARKS
    # ========================================================

    attemptable_marks = 0
    attemptable_question_count = 0

    required_displayed_question_count = 0

    if pattern:

        sections = list(
            pattern.sections
            .all()
            .order_by("display_order")
        )

        for section in sections:

            section_question_count = (
                section.number_of_questions or 0
            )

            required_displayed_question_count += (
                section_question_count
            )

            section_marks = section.marks or 0

            attempt_rule = str(
                section.attempt_rule or ""
            ).strip().lower()
            section_generated_count = sum(
                1
                for gq in generated_questions
                if (
                    gq.section_id == section.id
                    and gq.question_id is not None
                )
            )

            # ------------------------------------------------
            # Determine number of questions a student attempts
            # ------------------------------------------------

            attempt_count = section_question_count

            if attempt_rule == "1of2":
                attempt_count = 1

            elif attempt_rule == "2of3":
                attempt_count = 2

            elif attempt_rule == "3of4":
                attempt_count = 3

            elif attempt_rule == "4of5":
                attempt_count = 4

            elif attempt_rule == "5of5":
                attempt_count = 5

            elif attempt_rule == "custom":
                # For custom rules we cannot safely guess.
                attempt_count = section_question_count

            elif (
                "every question" in attempt_rule
                or "attempt every" in attempt_rule
            ):
                attempt_count = section_question_count

            # ------------------------------------------------
            # Prevent impossible values
            # ------------------------------------------------

            attempt_count = min(
                attempt_count,
                section_question_count
            )

            # ------------------------------------------------
            # Attemptable questions
            # ------------------------------------------------

            actual_attempt_count = min(
                attempt_count,
                section_generated_count
            )

            attemptable_question_count += (
                actual_attempt_count
            )

            # ------------------------------------------------
            # Attemptable marks
            # ------------------------------------------------

            attemptable_marks += (
                actual_attempt_count * section_marks
            )

    # ========================================================
    # MARKS STATUS
    # ========================================================

    if required_marks is None:

        marks_status = "unknown"

    elif attemptable_marks == required_marks:

        marks_status = "correct"

    elif attemptable_marks < required_marks:

        marks_status = "below_required"

    else:

        marks_status = "above_required"

    # ========================================================
    # QUESTION COUNT STATUS
    # ========================================================

    if required_displayed_question_count == 0:

        question_count_status = "unknown"

    elif (
        displayed_question_count
        == required_displayed_question_count
    ):

        question_count_status = "correct"

    elif (
        displayed_question_count
        < required_displayed_question_count
    ):

        question_count_status = "below_required"

    else:

        question_count_status = "above_required"

    # ========================================================
    # RETURN
    # ========================================================

    return {
        # ====================================================
        # DISPLAYED VALUES
        # ====================================================

        "displayed_marks": displayed_marks,

        "displayed_question_count": (
            displayed_question_count
        ),

        # ====================================================
        # ATTEMPTABLE VALUES
        # ====================================================

        "attemptable_marks": attemptable_marks,

        "attemptable_question_count": (
            attemptable_question_count
        ),

        # ====================================================
        # BACKWARD-COMPATIBLE VALUES
        # ====================================================
        # These are required by run_rule_checks()

        "total_marks": attemptable_marks,

        "question_count": displayed_question_count,

        # ====================================================
        # PATTERN REQUIREMENTS
        # ====================================================

        "required_marks": required_marks,

        "required_question_count": (
            required_displayed_question_count
        ),

        # ====================================================
        # STATUS
        # ====================================================

        "marks_status": marks_status,

        "question_count_status": (
            question_count_status
        ),

        # ====================================================
        # DISTRIBUTIONS
        # ====================================================

        "unit_distribution": unit_distribution,

        "bloom_distribution": bloom_distribution,

        "difficulty_distribution": (
            difficulty_distribution
        ),

        "question_type_distribution": (
            question_type_distribution
        ),
    }


# ============================================================
# SIMILARITY / DUPLICATE DETECTION
# ============================================================

def detect_similar_questions(paper):
    """
    Compare every question with every other question
    using the existing question embeddings.

    Returns only pairs whose similarity is >= 70%.
    """

    generated_questions = get_paper_questions(paper)

    questions = [
        gq.question
        for gq in generated_questions
        if gq.question and gq.question.embedding
    ]

    similar_pairs = []

    for i in range(len(questions)):

        question_a = questions[i]

        for j in range(i + 1, len(questions)):

            question_b = questions[j]

            similarity = cosine_similarity(
                question_a.embedding,
                question_b.embedding
            )

            similarity_percentage = round(
                similarity * 100,
                2
            )

            if similarity >= SIMILARITY_THRESHOLD:

                if similarity >= DUPLICATE_THRESHOLD:
                    status = "duplicate"

                elif similarity >= 0.80:
                    status = "highly_similar"

                else:
                    status = "similar"

                similar_pairs.append({
                    "question_1_id": question_a.id,
                    "question_1": question_a.question_text,

                    "question_2_id": question_b.id,
                    "question_2": question_b.question_text,

                    "similarity": similarity_percentage,
                    "status": status,
                })

    # Highest similarity first
    similar_pairs.sort(
        key=lambda item: item["similarity"],
        reverse=True
    )

    return similar_pairs


# ============================================================
# DETERMINISTIC QUALITY CHECKS
# ============================================================

def run_rule_checks(metrics, similar_questions):
    """
    Perform deterministic quality checks.

    These checks are performed by Django/system rules.
    AI does not control or modify these results.
    """

    issues = []
    warnings = []
    passed = []

    # ========================================================
    # QUESTION COUNT
    # ========================================================

    question_count = metrics["question_count"]
    required_question_count = metrics["required_question_count"]

    if required_question_count:

        if question_count < required_question_count:

            issues.append({
                "type": "error",
                "category": "Question Count",
                "message": (
                    f"Paper contains {question_count} questions "
                    f"but {required_question_count} are required."
                )
            })

        elif question_count > required_question_count:

            warnings.append({
                "type": "warning",
                "category": "Question Count",
                "message": (
                    f"Paper contains {question_count} questions "
                    f"while the pattern expects "
                    f"{required_question_count}."
                )
            })

        else:

            passed.append({
                "category": "Question Count",
                "message": (
                    f"Question count is correct: "
                    f"{question_count}."
                )
            })

    else:

        if question_count == 0:

            issues.append({
                "type": "error",
                "category": "Question Count",
                "message": (
                    "The paper does not contain any questions."
                )
            })

        else:

            passed.append({
                "category": "Question Count",
                "message": (
                    f"{question_count} questions found."
                )
            })

    # ========================================================
    # TOTAL MARKS
    # ========================================================

    total_marks = metrics["attemptable_marks"]
    required_marks = metrics["required_marks"]
    marks_status = metrics["marks_status"]

    if marks_status == "below_required":

        issues.append({
            "type": "error",
            "category": "Total Marks",
            "message": (
                f"Paper has {total_marks} marks "
                f"but {required_marks} marks are required."
            )
        })

    elif marks_status == "above_required":

        warnings.append({
            "type": "warning",
            "category": "Total Marks",
            "message": (
                f"Paper has {total_marks} marks "
                f"while {required_marks} marks are required."
            )
        })

    elif marks_status == "correct":

        passed.append({
            "category": "Total Marks",
            "message": (
                f"Total marks are correct: "
                f"{total_marks}."
            )
        })

    else:

        if total_marks <= 0:

            issues.append({
                "type": "error",
                "category": "Total Marks",
                "message": (
                    "The paper has zero total marks."
                )
            })

        else:

            passed.append({
                "category": "Total Marks",
                "message": (
                    f"Total marks calculated: "
                    f"{total_marks}."
                )
            })

    # ========================================================
    # UNIT COVERAGE
    # ========================================================

    unit_distribution = metrics["unit_distribution"]

    if question_count == 0:

        warnings.append({
            "type": "warning",
            "category": "Unit Coverage",
            "message": (
                "Unit coverage cannot be evaluated because "
                "the paper contains no questions."
            )
        })

    elif len(unit_distribution) <= 1 and question_count > 1:

        warnings.append({
            "type": "warning",
            "category": "Unit Coverage",
            "message": (
                "Questions are concentrated in only one unit."
            )
        })

    else:

        passed.append({
            "category": "Unit Coverage",
            "message": (
                f"{len(unit_distribution)} unit(s) represented."
            )
        })

    # ========================================================
    # DIFFICULTY
    # ========================================================

    difficulty = metrics["difficulty_distribution"]

    if question_count == 0:

        warnings.append({
            "type": "warning",
            "category": "Difficulty",
            "message": (
                "Difficulty distribution cannot be evaluated "
                "because the paper contains no questions."
            )
        })

    elif difficulty["hard"] == 0 and question_count >= 5:

        warnings.append({
            "type": "warning",
            "category": "Difficulty",
            "message": (
                "No Hard-level questions were found."
            )
        })

    else:

        passed.append({
            "category": "Difficulty",
            "message": (
                "Difficulty levels are represented."
            )
        })

    # ========================================================
    # BLOOM'S TAXONOMY
    # ========================================================

    bloom = metrics["bloom_distribution"]

    higher_order_count = (
        bloom["3"]
        + bloom["4"]
        + bloom["5"]
        + bloom["6"]
    )

    if question_count == 0:

        warnings.append({
            "type": "warning",
            "category": "Bloom's Taxonomy",
            "message": (
                "Bloom's Taxonomy distribution cannot be "
                "evaluated because the paper contains no questions."
            )
        })

    elif (
        question_count >= 5
        and higher_order_count == 0
    ):

        warnings.append({
            "type": "warning",
            "category": "Bloom's Taxonomy",
            "message": (
                "No Apply, Analyze, Evaluate, or Create "
                "questions were found."
            )
        })

    else:

        passed.append({
            "category": "Bloom's Taxonomy",
            "message": (
                "Bloom levels are represented."
            )
        })

    # ========================================================
    # QUESTION TYPE
    # ========================================================

    question_types = metrics[
        "question_type_distribution"
    ]

    active_types = [
        value
        for value in question_types.values()
        if value > 0
    ]

    if question_count == 0:

        warnings.append({
            "type": "warning",
            "category": "Question Type",
            "message": (
                "Question type distribution cannot be evaluated "
                "because the paper contains no questions."
            )
        })

    elif (
        question_count >= 5
        and len(active_types) == 1
    ):

        warnings.append({
            "type": "warning",
            "category": "Question Type",
            "message": (
                "The paper contains only one question type."
            )
        })

    else:

        passed.append({
            "category": "Question Type",
            "message": (
                "Question types are represented."
            )
        })

    # ========================================================
    # SIMILAR / DUPLICATE QUESTIONS
    # ========================================================

    duplicates = [
        item
        for item in similar_questions
        if item["status"] == "duplicate"
    ]

    highly_similar = [
        item
        for item in similar_questions
        if item["status"] == "highly_similar"
    ]

    similar = [
        item
        for item in similar_questions
        if item["status"] == "similar"
    ]

    # --------------------------------------------------------
    # DUPLICATES
    # --------------------------------------------------------

    if duplicates:

        issues.append({
            "type": "error",
            "category": "Duplicate Questions",
            "message": (
                f"{len(duplicates)} duplicate "
                f"question pair(s) detected."
            )
        })

    # --------------------------------------------------------
    # HIGHLY SIMILAR
    # --------------------------------------------------------

    if highly_similar:

        warnings.append({
            "type": "warning",
            "category": "Question Similarity",
            "message": (
                f"{len(highly_similar)} highly similar "
                f"question pair(s) detected."
            )
        })

    # --------------------------------------------------------
    # MODERATELY SIMILAR
    # --------------------------------------------------------

    if similar:

        warnings.append({
            "type": "warning",
            "category": "Question Similarity",
            "message": (
                f"{len(similar)} similar "
                f"question pair(s) detected."
            )
        })

    # --------------------------------------------------------
    # NO SIMILARITY PROBLEMS
    # --------------------------------------------------------

    if not duplicates and not highly_similar and not similar:

        passed.append({
            "category": "Question Similarity",
            "message": (
                "No similar question pairs detected."
            )
        })

    # ========================================================
    # RETURN RESULTS
    # ========================================================

    return {
        "issues": issues,
        "warnings": warnings,
        "passed": passed,
    }


# ============================================================
# QUALITY SCORE
# ============================================================

def calculate_quality_score(rule_results):
    """
    Calculate a simple deterministic score.

    Start with 100.

    Error    -> -20
    Warning  -> -10

    Minimum score = 0
    """

    score = 100

    score -= (
        len(rule_results["issues"]) * 20
    )

    score -= (
        len(rule_results["warnings"]) * 10
    )

    score = max(
        0,
        min(100, score)
    )

    return score


# ============================================================
# PREPARE AI SUMMARY
# ============================================================

def prepare_ai_summary(
    paper,
    metrics,
    similar_questions,
    rule_results,
):
    """
    Create a compact summary for Qwen3.

    We do NOT send unnecessary database information.
    """

    generated_questions = get_paper_questions(paper)

    question_list = []

    for index, gq in enumerate(generated_questions, start=1):

        question = gq.question

        if not question:
            continue

        question_list.append({
            "number": index,
            "text": question.question_text,
            "marks": question.marks,
            "unit": question.unit,
            "bloom": question.bloom_level,
            "difficulty": question.difficulty,
            "type": question.question_type,
        })

    return {
        "paper_title": paper.title,

        "metrics": metrics,

        "rule_results": rule_results,

        "similar_questions": similar_questions,

        "questions": question_list,
    }


# ============================================================
# QWEN3 AI ANALYSIS
# ============================================================

def get_ai_quality_analysis(summary):
    """
    Send paper summary to local Qwen3:8b.

    AI provides intelligent observations and suggestions.

    It does NOT modify the paper.
    """

    prompt = f"""
You are an academic examination paper quality analyzer.

Analyze the following examination paper.

IMPORTANT RULES:

1. Do NOT change any question.
2. Do NOT invent statistics.
3. Use the supplied metrics as the source of truth.
4. Do NOT override Django rule checks.
5. Give practical suggestions for a teacher.
6. Be concise and clear.
7. Return ONLY valid JSON.
8. Do not use markdown.

Paper data:

{json.dumps(summary, indent=2)}

Return exactly this JSON structure:

{{
    "overall_comment": "Short overall assessment of the paper.",

    "strengths": [
        "Strength 1",
        "Strength 2"
    ],

    "concerns": [
        "Concern 1",
        "Concern 2"
    ],

    "suggestions": [
        "Suggestion 1",
        "Suggestion 2"
    ]
}}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        },
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    text = data.get(
        "response",
        ""
    ).strip()

    if not text:
        raise ValueError(
            "Ollama returned an empty response."
        )

    result = json.loads(text)

    return {
        "overall_comment": str(
            result.get(
                "overall_comment",
                ""
            )
        ).strip(),

        "strengths": result.get(
            "strengths",
            []
        ),

        "concerns": result.get(
            "concerns",
            []
        ),

        "suggestions": result.get(
            "suggestions",
            []
        ),
    }


# ============================================================
# MAIN QUALITY CHECKER
# ============================================================

def check_paper_quality(paper):
    """
    Main function.

    This is the function our API will call.

    Flow:

    Paper
      ↓
    Metrics
      ↓
    Similarity
      ↓
    Rule Checks
      ↓
    Score
      ↓
    Qwen3
      ↓
    Final Quality Report
    """

    # --------------------------------------------------------
    # STEP 1: Deterministic metrics
    # --------------------------------------------------------

    metrics = calculate_basic_metrics(
        paper
    )

    # --------------------------------------------------------
    # STEP 2: Similarity detection
    # --------------------------------------------------------

    similar_questions = detect_similar_questions(
        paper
    )

    # --------------------------------------------------------
    # STEP 3: Rule checks
    # --------------------------------------------------------

    rule_results = run_rule_checks(
        metrics,
        similar_questions
    )

    # --------------------------------------------------------
    # STEP 4: Score
    # --------------------------------------------------------

    quality_score = calculate_quality_score(
        rule_results
    )

    # --------------------------------------------------------
    # STEP 5: Prepare AI input
    # --------------------------------------------------------

    ai_summary = prepare_ai_summary(
        paper,
        metrics,
        similar_questions,
        rule_results,
    )

    # --------------------------------------------------------
    # STEP 6: Qwen3 analysis
    # --------------------------------------------------------

    try:

        ai_analysis = get_ai_quality_analysis(
            ai_summary
        )

        ai_available = True

    except Exception as exc:

        ai_analysis = {
            "overall_comment": (
                "AI analysis could not be completed. "
                "The deterministic quality checks are still available."
            ),

            "strengths": [],

            "concerns": [
                f"AI analysis error: {str(exc)}"
            ],

            "suggestions": [],
        }

        ai_available = False

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    return {
        "success": True,

        "quality_score": quality_score,

        "metrics": metrics,

        "similar_questions": similar_questions,

        "rule_results": rule_results,

        "ai_analysis": ai_analysis,

        "ai_available": ai_available,
    }