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

# V2 TF-IDF vectorizer
TFIDF_PATH = os.path.join(
    MODEL_DIR,
    "difficulty_tfidf_v2.joblib"
)

# V2 difficulty classifier
MODEL_PATH = os.path.join(
    MODEL_DIR,
    "difficulty_classifier_v2.joblib"
)


# ============================================================
# LOAD V2 MODEL
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

    # Predict difficulty using V2 model
    prediction = model.predict(
        question_vector
    )[0]

    return str(
        prediction
    ).lower()