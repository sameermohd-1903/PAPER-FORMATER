import os
import joblib


# ============================================================
# ML MODEL PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "ml_models"
)

TFIDF_PATH = os.path.join(
    MODEL_DIR,
    "difficulty_tfidf.joblib"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "difficulty_classifier.joblib"
)


# ============================================================
# LOAD MODEL
# ============================================================

tfidf = joblib.load(TFIDF_PATH)

model = joblib.load(MODEL_PATH)


# ============================================================
# PREDICT DIFFICULTY
# ============================================================

def predict_difficulty(question_text):
    """
    Predict difficulty of a question.

    Returns:
        easy
        medium
        hard
    """

    if not question_text:
        raise ValueError(
            "Question text cannot be empty."
        )

    question_text = str(
        question_text
    ).strip()

    if not question_text:
        raise ValueError(
            "Question text cannot be empty."
        )

    # Convert question into TF-IDF features
    question_vector = tfidf.transform(
        [question_text]
    )

    # Predict difficulty
    prediction = model.predict(
        question_vector
    )[0]

    return str(
        prediction
    ).lower()