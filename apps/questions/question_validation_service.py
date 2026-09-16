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
    value = str(value or "").strip().lower()

    if value in {
        "cs",
        "case study",
        "case-study",
        "case_study",
    }:
        return "casestudy"

    if value in {
        "multiple choice",
        "multiple choice questions",
    }:
        return "mcq"

    if value in {
        "following the questions",
        "following questions",
    }:
        return "ftq"

    return value


def normalize_difficulty(value):
    return str(value or "").strip().lower()


def normalize_bloom_level(value):
    return str(value or "").strip()


# =========================================================
# VALIDATE INPUT
# =========================================================

def validate_input(
    question_text,
    subject,
    unit,
    marks,
    bloom_level,
    difficulty,
    question_type,
):
    """
    Validate the values before sending the question
    to the AI validator.
    """

    errors = []

    question_text = str(question_text or "").strip()

    if not question_text:
        errors.append("Question text is required.")

    if len(question_text) < 10:
        errors.append(
            "Question text is too short."
        )

    subject = str(subject or "").strip()

    if not subject:
        errors.append("Subject is required.")

    unit = str(unit or "").strip()

    if not unit:
        errors.append("Unit is required.")

    try:
        marks = int(marks)

        if marks <= 0:
            errors.append(
                "Marks must be greater than 0."
            )

    except (TypeError, ValueError):
        errors.append(
            "Marks must be a valid positive integer."
        )

    bloom_level = normalize_bloom_level(
        bloom_level
    )

    if bloom_level not in VALID_BLOOM_LEVELS:
        errors.append(
            "Invalid Bloom level."
        )

    difficulty = normalize_difficulty(
        difficulty
    )

    if difficulty not in VALID_DIFFICULTIES:
        errors.append(
            "Invalid difficulty."
        )

    question_type = normalize_question_type(
        question_type
    )

    if question_type not in VALID_QUESTION_TYPES:
        errors.append(
            "Invalid question type."
        )

    if errors:
        raise ValueError(
            " | ".join(errors)
        )

    return {
        "question_text": question_text,
        "subject": subject,
        "unit": unit,
        "marks": marks,
        "bloom_level": bloom_level,
        "difficulty": difficulty,
        "question_type": question_type,
    }


# =========================================================
# BUILD VALIDATION PROMPT
# =========================================================

def build_validation_prompt(
    question_text,
    subject,
    unit,
    marks,
    bloom_level,
    difficulty,
    question_type,
):
    """
    Create a strict validation prompt for Qwen3.
    """

    bloom_name = VALID_BLOOM_LEVELS[
        bloom_level
    ]

    prompt = f"""
You are an expert university examination
question evaluator.

Your task is to VALIDATE the following question.

QUESTION:
{question_text}

REQUESTED REQUIREMENTS:

Subject: {subject}
Unit: {unit}
Marks: {marks}
Bloom Level: {bloom_level} - {bloom_name}
Difficulty: {difficulty}
Question Type: {question_type}


==================================================
VALIDATION RULES
==================================================

1. SUBJECT RELEVANCE

Check whether the question is relevant to:

Subject: {subject}

Return true if relevant.
Return false if unrelated.


2. UNIT RELEVANCE

Check whether the question is relevant to:

Unit: {unit}

Return true if the question clearly belongs
to the requested unit.

Do not assume relevance merely because the
subject is correct.


3. BLOOM LEVEL

Determine the ACTUAL cognitive level required
to answer the question.

Requested Bloom level:
{bloom_level} - {bloom_name}

Use these definitions:

1 - Remember:
Recall facts, definitions, terms, or basic information.

2 - Understand:
Explain, summarize, describe, interpret, or classify.

3 - Apply:
Use knowledge, rules, methods, or procedures
to solve a problem or perform a task.

4 - Analyze:
Break information into parts, identify relationships,
compare structures, examine causes, or distinguish components.

5 - Evaluate:
Make a judgment or decision using explicit criteria,
evidence, justification, or critical reasoning.

6 - Create:
Design, construct, formulate, develop, or produce
something new.


IMPORTANT:

Judge the actual task of the question.

Do NOT classify a question only because it contains
words such as:

"explain"
"analyze"
"apply"
"evaluate"

The cognitive task must actually match the Bloom level.


4. DIFFICULTY

Determine whether the question is:

easy
medium
hard

based on the knowledge, reasoning, steps,
and complexity required to answer it.

Requested difficulty:
{difficulty}


5. QUESTION TYPE

Requested type:
{question_type}

For MCQ:
- Must contain a clear question.
- Must contain four options A), B), C), D).
- There should be one clearly correct answer.

For FTQ:
- It should be a normal theoretical/descriptive
  or problem-solving question.
- It should not require MCQ options.

For Case Study:
- It should contain a meaningful scenario/context.
- The question should require applying, analyzing,
  evaluating, or creating according to the requested
  Bloom level.


6. MARKS SUITABILITY

Requested marks:
{marks}

Determine whether the amount of work and reasoning
required is reasonably suitable for {marks} marks.

Do not require an exact word count.

Consider:
- complexity
- number of concepts
- reasoning required
- expected answer length
- number of steps


7. QUESTION QUALITY

Check whether the question:

- is complete
- is understandable
- is academically meaningful
- has enough information to answer
- is not ambiguous
- does not contain obvious contradictions
- is suitable for a university examination


==================================================
FINAL DECISION
==================================================

The question is VALID only when the important
requirements are satisfied.

Return:

valid = true

only when the question adequately satisfies
the requested requirements.

Otherwise:

valid = false


==================================================
OUTPUT FORMAT
==================================================

Return ONLY valid JSON.

Do not include markdown.
Do not include explanations outside JSON.

Use exactly this structure:

{{
    "valid": true,
    "subject_relevant": true,
    "unit_relevant": true,
    "bloom_match": true,
    "actual_bloom_level": "3",
    "difficulty_match": true,
    "actual_difficulty": "medium",
    "type_match": true,
    "marks_suitable": true,
    "quality_ok": true,
    "confidence": 0.95,
    "issues": [],
    "reason": "Short explanation"
}}

If invalid, use:

{{
    "valid": false,
    "subject_relevant": true,
    "unit_relevant": false,
    "bloom_match": false,
    "actual_bloom_level": "2",
    "difficulty_match": true,
    "actual_difficulty": "medium",
    "type_match": true,
    "marks_suitable": true,
    "quality_ok": true,
    "confidence": 0.90,
    "issues": [
        "Question does not match the requested Bloom level.",
        "Question does not appear relevant to the requested unit."
    ],
    "reason": "Short explanation"
}}

Now validate the question.
"""

    return prompt.strip()


# =========================================================
# EXTRACT JSON
# =========================================================

def extract_json(response_text):
    """
    Safely extract JSON from Qwen3 response.
    """

    if not response_text:
        raise ValueError(
            "Ollama returned an empty response."
        )

    text = response_text.strip()

    # Remove markdown code fences
    if text.startswith("```"):

        lines = text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

        if text.lower().startswith("json"):
            text = text[4:].strip()

    # Try direct JSON
    try:
        return json.loads(text)

    except json.JSONDecodeError:
        pass

    # Try extracting JSON object
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(
            "No valid JSON object found in AI response."
        )

    json_text = text[start:end + 1]

    try:

        return json.loads(json_text)

    except json.JSONDecodeError as exc:

        raise ValueError(
            f"Invalid JSON returned by Ollama: {exc}"
        ) from exc


# =========================================================
# CALL OLLAMA
# =========================================================

def call_ollama(prompt):
    """
    Call local Ollama/Qwen3.
    """

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.0,
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
            f"Unable to connect to Ollama: {exc}"
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
            "Ollama returned an invalid HTTP response."
        ) from exc

    result = data.get("response")

    if not result:

        raise RuntimeError(
            "Ollama response is missing 'response'."
        )

    return result


# =========================================================
# DETERMINISTIC BLOOM SAFETY CHECK
# =========================================================

def detect_obvious_bloom_level(question_text):
    """
    Detect obvious Bloom-level signals.

    This is NOT a complete Bloom classifier.
    It is only a safety layer for very obvious cases.
    """

    text = str(question_text or "").strip().lower()

    # Bloom 1 - Remember
    remember_patterns = [
        "define ",
        "what is ",
        "what are ",
        "list ",
        "name ",
        "state ",
        "identify ",
        "recall ",
    ]

    for pattern in remember_patterns:
        if text.startswith(pattern):
            return "1"

    # Bloom 2 - Understand
    understand_patterns = [
        "explain ",
        "describe ",
        "summarize ",
        "differentiate between ",
        "compare ",
    ]

    for pattern in understand_patterns:
        if text.startswith(pattern):
            return "2"

    # Bloom 3 - Apply
    apply_patterns = [
        "apply ",
        "calculate ",
        "solve ",
        "use ",
        "implement ",
        "demonstrate ",
        "given ",
    ]

    for pattern in apply_patterns:
        if text.startswith(pattern):
            return "3"

    # No obvious pattern detected
    return None






# =========================================================
# NORMALIZE AI RESULT
# =========================================================

def normalize_validation_result(
    result,
    requested_bloom,
    requested_difficulty,
    requested_type,
    question_text,
):
    """
    Normalize and validate the AI validator output.
    """

    if not isinstance(result, dict):

        raise ValueError(
            "AI validation result must be a JSON object."
        )

    actual_bloom = normalize_bloom_level(
        result.get("actual_bloom_level")
    )
    
    obvious_bloom = detect_obvious_bloom_level(
        question_text
    )

    actual_difficulty = normalize_difficulty(
        result.get("actual_difficulty")
    )

    actual_type = normalize_question_type(
        result.get("actual_question_type")
    )

    # Some models may omit actual question type.
    # In that case use the explicit type_match result.
    type_match = bool(
        result.get("type_match", False)
    )

    bloom_match = bool(
        result.get("bloom_match", False)
    )

    difficulty_match = bool(
        result.get("difficulty_match", False)
    )

    subject_relevant = bool(
        result.get("subject_relevant", False)
    )

    unit_relevant = bool(
        result.get("unit_relevant", False)
    )

    marks_suitable = bool(
        result.get("marks_suitable", False)
    )

    quality_ok = bool(
        result.get("quality_ok", False)
    )

    valid = bool(
        result.get("valid", False)
    )

    issues = result.get("issues", [])

    if not isinstance(issues, list):
        issues = [str(issues)]

    issues = [
        str(issue).strip()
        for issue in issues
        if str(issue).strip()
    ]

    # -----------------------------------------------------
    # Deterministic safety checks
    # -----------------------------------------------------

    # -----------------------------------------------------
    # Deterministic Bloom safety check
    # -----------------------------------------------------

    if obvious_bloom:

    # The deterministic safety layer has detected
    # an obvious Bloom level from the actual question.
        actual_bloom = obvious_bloom

    # The requested Bloom level MUST match it.
        bloom_match = (
            obvious_bloom == requested_bloom
        )
    if not bloom_match:
            issues.append(
                f"Question appears to be Bloom level "
                f"{obvious_bloom}, which does not match the requested level {requested_bloom}."
            )    

    elif actual_bloom:

    # If there is no obvious keyword-level signal,
    # use the AI evaluator's result.
        bloom_match = (
            actual_bloom == requested_bloom
        )

    else:

    # If neither the deterministic checker nor AI
    # can determine the Bloom level, reject it.
        bloom_match = False

    if actual_difficulty:
        if actual_difficulty != requested_difficulty:
            difficulty_match = False

    # If AI supplied an actual type, verify it.
    if actual_type:
        if actual_type != requested_type:
            type_match = False

    # Final validity is calculated from the important checks.
    final_valid = all([
        subject_relevant,
        unit_relevant,
        bloom_match,
        difficulty_match,
        type_match,
        marks_suitable,
        quality_ok,
    ])

    # AI cannot override deterministic checks.
    valid = valid and final_valid

    return {
        "valid": valid,
        "subject_relevant": subject_relevant,
        "unit_relevant": unit_relevant,
        "bloom_match": bloom_match,
        "requested_bloom_level": requested_bloom,
        "actual_bloom_level": actual_bloom or None,
        "difficulty_match": difficulty_match,
        "requested_difficulty": requested_difficulty,
        "actual_difficulty": actual_difficulty or None,
        "type_match": type_match,
        "requested_question_type": requested_type,
        "marks_suitable": marks_suitable,
        "quality_ok": quality_ok,
        "confidence": result.get(
            "confidence",
            0.0
        ),
        "issues": issues,
        "reason": str(
            result.get("reason", "")
        ).strip(),
    }


# =========================================================
# MAIN VALIDATION FUNCTION
# =========================================================

def validate_generated_question(
    question_text,
    subject,
    unit,
    marks,
    bloom_level,
    difficulty,
    question_type,
):
    """
    Validate a generated question using Qwen3.

    This function DOES NOT save anything
    to the database.
    """

    requirements = validate_input(
        question_text=question_text,
        subject=subject,
        unit=unit,
        marks=marks,
        bloom_level=bloom_level,
        difficulty=difficulty,
        question_type=question_type,
    )

    prompt = build_validation_prompt(
        question_text=requirements["question_text"],
        subject=requirements["subject"],
        unit=requirements["unit"],
        marks=requirements["marks"],
        bloom_level=requirements["bloom_level"],
        difficulty=requirements["difficulty"],
        question_type=requirements["question_type"],
    )

    raw_response = call_ollama(prompt)

    result = extract_json(raw_response)

    validation = normalize_validation_result(
        result=result,
        requested_bloom=requirements["bloom_level"],
        requested_difficulty=requirements["difficulty"],
        requested_type=requirements["question_type"],
        question_text=requirements["question_text"]
    )

    return validation