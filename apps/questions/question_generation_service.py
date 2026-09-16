import json
import os
import requests


# =========================================================
# OLLAMA CONFIGURATION
# =========================================================

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://127.0.0.1:11434/api/generate"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen3:8b"
)

OLLAMA_TIMEOUT = int(
    os.getenv("OLLAMA_TIMEOUT", "120")
)


# =========================================================
# VALID VALUES
# =========================================================

VALID_BLOOM_LEVELS = {
    "1": "Remember",
    "2": "Understand",
    "3": "Apply",
    "4": "Analyze",
    "5": "Evaluate",
    "6": "Create",
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


# =========================================================
# NORMALIZATION
# =========================================================

def normalize_question_type(value):
    """
    Convert different representations of question type
    into the standard values used by the project.
    """

    value = str(value or "").strip().lower()

    if value in {"cs", "case study", "case-study", "case_study"}:
        return "casestudy"

    if value in {"multiple choice", "multiple choice questions"}:
        return "mcq"

    if value in {"following the questions", "following questions"}:
        return "ftq"

    return value


def normalize_difficulty(value):
    return str(value or "").strip().lower()


def normalize_bloom_level(value):
    return str(value or "").strip()


# =========================================================
# VALIDATE GENERATION REQUIREMENTS
# =========================================================

def validate_generation_requirements(
    subject,
    unit,
    marks,
    bloom_level,
    difficulty,
    question_type,
):
    """
    Validate the requirements before calling Ollama.
    """

    errors = []

    if not str(subject or "").strip():
        errors.append("Subject is required.")

    if not str(unit or "").strip():
        errors.append("Unit is required.")

    try:
        marks = int(marks)
        if marks <= 0:
            errors.append("Marks must be greater than 0.")
    except (TypeError, ValueError):
        errors.append("Marks must be a valid positive integer.")

    bloom_level = normalize_bloom_level(bloom_level)

    if bloom_level not in VALID_BLOOM_LEVELS:
        errors.append(
            "Bloom level must be one of: "
            + ", ".join(VALID_BLOOM_LEVELS.keys())
        )

    difficulty = normalize_difficulty(difficulty)

    if difficulty not in VALID_DIFFICULTIES:
        errors.append(
            "Difficulty must be one of: "
            + ", ".join(sorted(VALID_DIFFICULTIES))
        )

    question_type = normalize_question_type(question_type)

    if question_type not in VALID_QUESTION_TYPES:
        errors.append(
            "Question type must be one of: "
            + ", ".join(sorted(VALID_QUESTION_TYPES))
        )

    if errors:
        raise ValueError(" | ".join(errors))

    return {
        "subject": str(subject).strip(),
        "unit": str(unit).strip(),
        "marks": marks,
        "bloom_level": bloom_level,
        "difficulty": difficulty,
        "question_type": question_type,
    }


# =========================================================
# BUILD GENERATION PROMPT
# =========================================================

def build_generation_prompt(
    subject,
    unit,
    marks,
    bloom_level,
    difficulty,
    question_type,
):
    """
    Build a strict prompt for Qwen3.
    """

    bloom_name = VALID_BLOOM_LEVELS[bloom_level]

    if question_type == "mcq":

        type_instruction = """
Generate exactly one Multiple Choice Question.

The question must contain exactly four options:
A)
B)
C)
D)

Also provide the correct option.
"""

    elif question_type == "casestudy":

        type_instruction = """
Generate one case-study based question.

Provide a realistic short scenario related to the subject
and then ask the student to analyze/apply/evaluate it
according to the requested Bloom level.
"""

    else:

        type_instruction = """
Generate one normal theoretical/descriptive question.
Do not generate MCQ options.
"""

    prompt = f"""
You are an expert university examination question setter.

Generate ONE high-quality examination question.

STRICT REQUIREMENTS:

Subject: {subject}
Unit: {unit}
Marks: {marks}
Bloom Level: {bloom_level} - {bloom_name}
Difficulty: {difficulty}
Question Type: {question_type}

{type_instruction}

BLOOM LEVEL REQUIREMENT:

The question must genuinely test the requested Bloom level.
Do not merely use words such as "explain", "analyze", or
"apply" unless the actual task matches that cognitive level.

DIFFICULTY REQUIREMENT:

The question must genuinely match the requested difficulty:
{difficulty}.

MARKS REQUIREMENT:

The question must be appropriate for {marks} marks.

UNIT REQUIREMENT:

The question must be directly related to Unit {unit}
of the subject.

IMPORTANT:

- Generate only ONE question.
- Do not include introductory explanation.
- Do not include unnecessary text.
- Do not mention these instructions.
- Do not generate multiple alternative questions.
- Do not use markdown.
- Return ONLY valid JSON.

JSON FORMAT:

{{
    "question_text": "generated question here"
}}

For MCQ, use:

{{
    "question_text": "question text with A), B), C), D) options"
}}

Now generate the question.
"""

    return prompt.strip()


# =========================================================
# EXTRACT JSON FROM OLLAMA RESPONSE
# =========================================================

def extract_json(response_text):
    """
    Extract JSON safely from the Ollama response.

    Qwen may occasionally return JSON surrounded by
    extra whitespace or code fences.
    """

    if not response_text:
        raise ValueError(
            "Ollama returned an empty response."
        )

    text = response_text.strip()

    # Remove markdown code fences if present
    if text.startswith("```"):
        lines = text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

        if text.lower().startswith("json"):
            text = text[4:].strip()

    # Try complete JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting the first JSON object
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError(
            "Unable to find valid JSON in Ollama response."
        )

    json_text = text[start:end + 1]

    try:
        return json.loads(json_text)

    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Ollama returned invalid JSON: {exc}"
        ) from exc


# =========================================================
# CALL OLLAMA
# =========================================================

def call_ollama(prompt):
    """
    Send the generation prompt to local Ollama.
    """

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.2,
        },
    }

    try:

        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=OLLAMA_TIMEOUT,
        )

    except requests.RequestException as exc:

        raise RuntimeError(
            f"Unable to connect to Ollama at "
            f"{OLLAMA_URL}: {exc}"
        ) from exc

    if response.status_code != 200:

        raise RuntimeError(
            f"Ollama returned HTTP "
            f"{response.status_code}: "
            f"{response.text[:500]}"
        )

    try:
        data = response.json()

    except ValueError as exc:

        raise RuntimeError(
            "Ollama returned a non-JSON HTTP response."
        ) from exc

    response_text = data.get("response", "")

    if not response_text:

        raise RuntimeError(
            "Ollama response did not contain "
            "a generated answer."
        )

    return response_text


# =========================================================
# VALIDATE GENERATED QUESTION
# =========================================================

def validate_generated_question(
    question_text,
    question_type,
):
    """
    Basic deterministic validation of the generated question.
    """

    question_text = str(
        question_text or ""
    ).strip()

    if not question_text:

        raise ValueError(
            "AI generated an empty question."
        )

    if len(question_text) < 10:

        raise ValueError(
            "AI generated question is too short."
        )

    if question_type == "mcq":

        required_options = [
            "A)",
            "B)",
            "C)",
            "D)",
        ]

        missing_options = [
            option
            for option in required_options
            if option not in question_text
        ]

        if missing_options:

            raise ValueError(
                "Generated MCQ is missing option(s): "
                + ", ".join(missing_options)
            )

    return question_text


# =========================================================
# GENERATE QUESTION
# =========================================================

def generate_question(
    subject,
    unit,
    marks,
    bloom_level,
    difficulty,
    question_type,
):
    """
    Generate one examination question using
    local Ollama + Qwen3.
    """

    requirements = validate_generation_requirements(
        subject=subject,
        unit=unit,
        marks=marks,
        bloom_level=bloom_level,
        difficulty=difficulty,
        question_type=question_type,
    )

    prompt = build_generation_prompt(
        subject=requirements["subject"],
        unit=requirements["unit"],
        marks=requirements["marks"],
        bloom_level=requirements["bloom_level"],
        difficulty=requirements["difficulty"],
        question_type=requirements["question_type"],
    )

    raw_response = call_ollama(prompt)

    result = extract_json(raw_response)

    if not isinstance(result, dict):

        raise ValueError(
            "AI response must be a JSON object."
        )

    question_text = result.get(
        "question_text"
    )

    question_text = validate_generated_question(
        question_text,
        requirements["question_type"],
    )

    return {
        "question_text": question_text,

        # Return the requested metadata so that the
        # next validation phase can verify it.
        "subject": requirements["subject"],
        "unit": requirements["unit"],
        "marks": requirements["marks"],
        "bloom_level": requirements["bloom_level"],
        "difficulty": requirements["difficulty"],
        "question_type": requirements["question_type"],

        "model": OLLAMA_MODEL,
    }