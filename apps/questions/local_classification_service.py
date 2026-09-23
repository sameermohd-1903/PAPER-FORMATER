import re

from .ml_service import predict_difficulty


VALID_BLOOM_LEVELS = {"1", "2", "3", "4", "5", "6"}
VALID_QUESTION_TYPES = {"mcq", "ftq", "casestudy"}


def _looks_like_mcq(question_text):
    patterns = [
        r"\bA[\)\.:]\s+.+\bB[\)\.:]\s+.+",
        r"\bA\)\s+.+\bB\)\s+.+",
        r"\bA\.\s+.+\bB\.\s+.+",
        r"\(A\)\s+.+\(B\)\s+.+",
        r"\b1[\)\.:]\s+.+\b2[\)\.:]\s+.+",
    ]

    return any(
        re.search(pattern, question_text, re.IGNORECASE | re.DOTALL)
        for pattern in patterns
    )


def _looks_like_case_study(question_text):
    case_keywords = [
        "case study",
        "case-study",
        "scenario",
        "real-world situation",
        "real world situation",
        "consider the following situation",
        "consider the following case",
        "given the following situation",
        "given the following case",
    ]

    text = question_text.lower()

    return any(keyword in text for keyword in case_keywords)


def _detect_bloom_level(question_text):
    text = question_text.lower().strip()

    # Level 6 - Create
    level_6_patterns = [
        r"\bdesign\b",
        r"\bdevelop\b",
        r"\bcreate\b",
        r"\bconstruct\b",
        r"\bbuild\b",
        r"\bformulate\b",
        r"\bpropose\b",
        r"\bdevelop a\b",
        r"\bdesign a\b",
        r"\bdesign an\b",
        r"\bcreate a\b",
        r"\bcreate an\b",
    ]

    if any(re.search(pattern, text) for pattern in level_6_patterns):
        return "6"

    # Level 5 - Evaluate
    level_5_patterns = [
        r"\bevaluate\b",
        r"\bassess\b",
        r"\bjustify\b",
        r"\bcritique\b",
        r"\bdefend\b",
        r"\brecommend\b",
        r"\bjudge\b",
    ]

    if any(re.search(pattern, text) for pattern in level_5_patterns):
        return "5"

    # Level 4 - Analyze
    level_4_patterns = [
        r"\banalyze\b",
        r"\banalyse\b",
        r"\bcompare\b",
        r"\bdifferentiate\b",
        r"\bdistinguish\b",
        r"\bexamine\b",
        r"\bcontrast\b",
        r"\binvestigate\b",
    ]

    if any(re.search(pattern, text) for pattern in level_4_patterns):
        return "4"

    # Level 3 - Apply
    level_3_patterns = [
        r"\bapply\b",
        r"\bcalculate\b",
        r"\bsolve\b",
        r"\bimplement\b",
        r"\bdemonstrate\b",
        r"\bexecute\b",
        r"\bperform\b",
        r"\buse\b",
        r"\bwrite a program\b",
        r"\bwrite an algorithm\b",
    ]

    if any(re.search(pattern, text) for pattern in level_3_patterns):
        return "3"

    # Level 2 - Understand
    level_2_patterns = [
        r"\bexplain\b",
        r"\bdescribe\b",
        r"\bdiscuss\b",
        r"\bsummarize\b",
        r"\bsummarise\b",
        r"\binterpret\b",
        r"\billustrate\b",
        r"\bclarify\b",
    ]

    if any(re.search(pattern, text) for pattern in level_2_patterns):
        return "2"

    # Level 1 - Remember
    level_1_patterns = [
        r"^what is\b",
        r"^what are\b",
        r"^define\b",
        r"^list\b",
        r"^name\b",
        r"^identify\b",
        r"^state\b",
        r"^mention\b",
        r"^give the definition\b",
    ]

    if any(re.search(pattern, text) for pattern in level_1_patterns):
        return "1"

    return "1"


def _detect_question_type(question_text):
    if _looks_like_mcq(question_text):
        return "mcq"

    if _looks_like_case_study(question_text):
        return "casestudy"

    return "ftq"


def classify_question(question_text):
    """
    Classify a question without using Ollama or any API.

    Difficulty:
        Uses the trained ML model.

    Bloom level:
        Uses local rules.

    Question type:
        Uses local pattern detection.
    """

    question_text = str(question_text or "").strip()

    if not question_text:
        raise ValueError("Question text cannot be empty.")

    # Trained ML model
    difficulty = predict_difficulty(question_text)

    # Local rules
    bloom_level = _detect_bloom_level(question_text)
    question_type = _detect_question_type(question_text)

    # Validation
    if bloom_level not in VALID_BLOOM_LEVELS:
        raise ValueError(
            f"Invalid Bloom level generated: {bloom_level}"
        )

    if difficulty not in {"easy", "medium", "hard"}:
        raise ValueError(
            f"Invalid difficulty generated: {difficulty}"
        )

    if question_type not in VALID_QUESTION_TYPES:
        raise ValueError(
            f"Invalid question type generated: {question_type}"
        )

    return {
        "bloom_level": bloom_level,
        "difficulty": difficulty,
        "question_type": question_type,
    }