from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"


_model = None


def get_model():
    global _model

    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)

    return _model


def generate_embedding(text):
    """Generate a 384-dimensional embedding."""

    text = text.strip()

    if not text:
        raise ValueError(
            "Question text cannot be empty."
        )

    model = get_model()

    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return embedding.tolist()