from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


print("Loading AI model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("AI model loaded successfully.")


question_a = "What is a primary key?"
question_b = "Define primary key in DBMS."
question_c = "Explain deadlock in operating systems."


print("\nGenerating embeddings...")

embeddings = model.encode([
    question_a,
    question_b,
    question_c
])


similarity_ab = cosine_similarity(
    [embeddings[0]],
    [embeddings[1]]
)[0][0]


similarity_ac = cosine_similarity(
    [embeddings[0]],
    [embeddings[2]]
)[0][0]


print("\n--------------------------------")
print("QUESTION A")
print("--------------------------------")
print(question_a)

print("\n--------------------------------")
print("QUESTION B")
print("--------------------------------")
print(question_b)

print("\n--------------------------------")
print("QUESTION C")
print("--------------------------------")
print(question_c)

print("\n================================")
print("SIMILARITY RESULTS")
print("================================")

print(
    "A ↔ B:",
    round(similarity_ab * 100, 2),
    "%"
)

print(
    "A ↔ C:",
    round(similarity_ac * 100, 2),
    "%"
)

print("\nTest completed.")