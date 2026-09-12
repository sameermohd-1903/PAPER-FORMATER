import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

django.setup()


from apps.questions.models import Question
from apps.questions.embedding_service import generate_embedding
from apps.questions.similarity_service import find_similar_questions


new_question = "What is a primary key?"


print("Generating embedding...")

embedding = generate_embedding(
    new_question
)


print("Finding similar questions...")


questions = Question.objects.filter(
    embedding__isnull=False
)


matches = find_similar_questions(
    embedding,
    questions
)


print("\n================================")
print("NEW QUESTION")
print("================================")

print(new_question)


print("\n================================")
print("SIMILAR QUESTIONS")
print("================================")


if not matches:

    print("No similar questions found.")

else:

    for match in matches:

        print(
            f"\nSimilarity: "
            f"{match['similarity']}%"
        )

        print(
            f"Question ID: "
            f"{match['id']}"
        )

        print(
            f"Question: "
            f"{match['question_text']}"
        )