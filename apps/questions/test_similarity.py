from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


model = SentenceTransformer("all-MiniLM-L6-v2")


question_a = "What is a primary key?"
question_b = "Define primary key in DBMS."
question_c = "Explain deadlock in operating systems."


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


print("Question A:")
print(question_a)

print("\nQuestion B:")
print(question_b)

print("\nQuestion C:")
print(question_c)

print("\nA ↔ B similarity:", round(similarity_ab * 100, 2), "%")
print("A ↔ C similarity:", round(similarity_ac * 100, 2), "%")