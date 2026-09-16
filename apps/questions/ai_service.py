import json
import os
import re

import requests


OLLAMA_URL = os.environ.get(
    "OLLAMA_URL",
    "http://127.0.0.1:11434/api/generate"
)

OLLAMA_MODEL = os.environ.get(
    "OLLAMA_MODEL",
    "qwen3:8b"
)


VALID_BLOOM_LEVELS = {
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
}

VALID_DIFFICULTIES = {
    "easy",
    "medium",
    "hard",
}

VALID_QUESTION_TYPES = {
    "mcq",
    "ftq",
    "casestudy",
}


def _looks_like_mcq(question_text):
    """
    Deterministic MCQ detection.

    If the question clearly contains multiple-choice
    options, classify it as MCQ without relying only
    on the LLM.
    """

    text = str(question_text or "").strip()

    patterns = [
        r"\bA[\)\.:]\s+.+\bB[\)\.:]\s+.+",
        r"\bA\)\s+.+\bB\)\s+.+",
        r"\bA\.\s+.+\bB\.\s+.+",
        r"\(A\)\s+.+\(B\)\s+.+",
        r"\b1[\)\.:]\s+.+\b2[\)\.:]\s+.+",
    ]

    for pattern in patterns:

        if re.search(
            pattern,
            text,
            flags=re.IGNORECASE | re.DOTALL
        ):
            return True

    return False


def classify_question(question_text):
    """
    Classify an academic question using local
    Ollama + Qwen3.

    Returns:

    {
        "bloom_level": "1"..."6",
        "difficulty": "easy"|"medium"|"hard",
        "question_type": "mcq"|"ftq"|"casestudy"
    }
    """

    question_text = str(
        question_text or ""
    ).strip()

    if not question_text:

        raise ValueError(
            "Question text cannot be empty."
        )

    # ========================================================
    # DETERMINISTIC MCQ CHECK
    # ========================================================

    obvious_mcq = _looks_like_mcq(
        question_text
    )

    # ========================================================
    # PROMPT
    # ========================================================

    prompt = f"""
You are a STRICT academic question classification system.

Your task is to classify ONE question.

QUESTION:
{question_text}

========================================================
QUESTION TYPE
========================================================

Choose exactly ONE:

mcq
ftq
casestudy

Definitions:

mcq:
A question containing multiple answer choices/options.
Examples:
- Which of the following is a DBMS?
  A) MySQL
  B) HTML
  C) CSS
  D) Python

- Which key uniquely identifies a record?
  A) Foreign key
  B) Primary key
  C) Candidate key
  D) Alternate key

IMPORTANT:
If the question contains options such as
A), B), C), D), classify it as "mcq".

ftq:
A normal descriptive, theoretical, definition,
explanation, comparison, or application question
without multiple-choice options.

Examples:
- Define DBMS.
- What is a primary key?
- Explain the advantages of DBMS.
- Apply normalization to the given database schema.

casestudy:
A question based on a specific case, scenario,
real-world situation, or detailed problem statement.

========================================================
BLOOM'S TAXONOMY
========================================================

1 = Remember
2 = Understand
3 = Apply
4 = Analyze
5 = Evaluate
6 = Create

Use the cognitive action required by the question.

Examples:

Bloom 1 - Remember:
- Define DBMS.
- What is a primary key?
- List four advantages of DBMS.
- State the definition of normalization.

Bloom 2 - Understand:
- Explain the advantages of DBMS.
- Describe how a primary key works.
- Explain the difference between data and information.

Bloom 3 - Apply:
- Apply normalization to the following database schema.
- Use SQL to retrieve students with marks above 80.
- Demonstrate how a primary key can be used in this table.

Bloom 4 - Analyze:
- Analyze the given database schema.
- Compare the relationships between the entities.
- Analyze the causes of update anomalies.

Bloom 5 - Evaluate:
- Evaluate whether normalization is suitable for this database.
- Justify the choice of a primary key.
- Critically assess the database design.

Bloom 6 - Create:
- Design a database for a hospital management system.
- Create an ER diagram for the given system.
- Develop a normalized database schema.

IMPORTANT:
Do not automatically classify every explanation as
a higher Bloom level.

"Define", "What is", "State", "List", "Name"
normally indicate Bloom 1.

"Explain", "Describe", "Discuss"
normally indicate Bloom 2 unless the question
clearly requires a higher cognitive action.

"Apply", "Use", "Demonstrate"
normally indicate Bloom 3.

"Analyze"
normally indicates Bloom 4.

"Evaluate", "Justify", "Critically assess"
normally indicate Bloom 5.

"Design", "Create", "Develop"
normally indicate Bloom 6.

========================================================
DIFFICULTY
========================================================

Choose exactly:

easy
medium
hard

Easy:
- Definition
- Recall
- Listing
- Basic concept
- Direct factual question

Examples:
- Define DBMS.
- What is a primary key?
- List four advantages of DBMS.

Medium:
- Requires explanation
- Requires application of a concept
- Requires an example
- Requires multiple connected steps

Examples:
- Explain normalization with an example.
- Apply normalization to a database schema.

Hard:
- Complex analysis
- Multiple concepts
- Detailed case/scenario
- Advanced evaluation or design

Examples:
- Analyze a complex database schema and identify normalization problems.
- Design a complete database architecture for a hospital.

========================================================
IMPORTANT RULES
========================================================

1. Return ONLY valid JSON.

2. Do NOT return markdown.

3. Do NOT return explanations.

4. Do NOT return additional fields.

5. bloom_level MUST be one of:
   "1", "2", "3", "4", "5", "6"

6. difficulty MUST be one of:
   "easy", "medium", "hard"

7. question_type MUST be one of:
   "mcq", "ftq", "casestudy"

8. If A), B), C), D) options are present,
   question_type MUST be "mcq".

9. "Define" and "What is" questions should normally
   be Bloom level 1.

10. Simple factual questions should normally be easy.

Return exactly:

{{
    "bloom_level": "1",
    "difficulty": "easy",
    "question_type": "ftq"
}}
"""

    # ========================================================
    # OLLAMA REQUEST
    # ========================================================

    try:

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0
                }
            },
            timeout=120,
        )

        response.raise_for_status()

    except requests.exceptions.ConnectionError:

        raise RuntimeError(
            "Unable to connect to Ollama. "
            "Make sure Ollama is running."
        )

    except requests.exceptions.Timeout:

        raise RuntimeError(
            "Ollama classification timed out."
        )

    except requests.exceptions.RequestException as exc:

        raise RuntimeError(
            f"Ollama request failed: {exc}"
        )

    # ========================================================
    # READ RESPONSE
    # ========================================================

    data = response.json()

    result_text = str(
        data.get("response", "")
    ).strip()

    if not result_text:

        raise ValueError(
            "Ollama returned an empty classification."
        )

    try:

        result = json.loads(
            result_text
        )

    except json.JSONDecodeError:

        raise ValueError(
            "Ollama returned invalid JSON."
        )

    # ========================================================
    # EXTRACT VALUES
    # ========================================================

    bloom_level = str(
        result.get(
            "bloom_level",
            ""
        )
    ).strip()

    difficulty = str(
        result.get(
            "difficulty",
            ""
        )
    ).strip().lower()

    question_type = str(
        result.get(
            "question_type",
            ""
        )
    ).strip().lower()

    # ========================================================
    # NORMALIZE QUESTION TYPE
    # ========================================================

    if question_type in {
        "case study",
        "case-study",
        "case_study",
        "cs",
    }:

        question_type = "casestudy"

    elif question_type in {
        "multiple choice",
        "multiple choice question",
        "multiple choice questions",
        "multiple-choice",
        "multiple-choice question",
        "multiple-choice questions",
    }:

        question_type = "mcq"

    elif question_type in {
        "following the questions",
        "following question",
        "descriptive",
        "theory",
        "theoretical",
        "subjective",
    }:

        question_type = "ftq"

    # ========================================================
    # HARD OVERRIDE FOR OBVIOUS MCQ
    # ========================================================

    if obvious_mcq:

        question_type = "mcq"

    # ========================================================
    # VALIDATE BLOOM
    # ========================================================

    if bloom_level not in VALID_BLOOM_LEVELS:

        raise ValueError(
            f"Invalid Bloom level returned by AI: "
            f"{bloom_level}"
        )

    # ========================================================
    # VALIDATE DIFFICULTY
    # ========================================================

    if difficulty not in VALID_DIFFICULTIES:

        raise ValueError(
            f"Invalid difficulty returned by AI: "
            f"{difficulty}"
        )

    # ========================================================
    # VALIDATE QUESTION TYPE
    # ========================================================

    if question_type not in VALID_QUESTION_TYPES:

        raise ValueError(
            f"Invalid question type returned by AI: "
            f"{question_type}"
        )

    # ========================================================
    # RETURN
    # ========================================================

    return {
        "bloom_level": bloom_level,
        "difficulty": difficulty,
        "question_type": question_type,
    }