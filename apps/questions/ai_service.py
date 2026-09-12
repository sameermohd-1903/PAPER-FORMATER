import json
import os



client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)


def classify_question(question_text):
    """
    Analyze a question and return:
    - Bloom level
    - Difficulty
    - Question type
    """

    prompt = f"""
You are an educational question classification system.

Analyze the following academic question.

Question:
{question_text}

Classify it using ONLY these values.

Bloom Level:
1 = Remember
2 = Understand
3 = Apply
4 = Analyze
5 = Evaluate
6 = Create

Difficulty:
easy
medium
hard

Question Type:
mcq
ftq
cs

Rules:

- mcq means Multiple Choice Question.
- ftq means a normal descriptive/following-the-question type question.
- cs means a Case Study type question.
- Return ONLY valid JSON.
- Do not add explanations.

Required JSON format:

{{
    "bloom_level": "1",
    "difficulty": "easy",
    "question_type": "ftq"
}}
"""

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=prompt,
    )

    text = response.output_text.strip()

    # Remove markdown code fences if the model returns them
    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    result = json.loads(text)

    return result