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


def generate_embeddings_batch(texts):
    """Generate embeddings for multiple questions at once."""

    if not texts:
        return []

    cleaned_texts = [
        str(text).strip()
        for text in texts
    ]

    if any(not text for text in cleaned_texts):
        raise ValueError(
            "Question text cannot be empty."
        )

    model = get_model()

    embeddings = model.encode(
        cleaned_texts,
        batch_size=32,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    return embeddings.tolist()