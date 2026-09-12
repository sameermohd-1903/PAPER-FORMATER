from django.core.management.base import BaseCommand

from apps.questions.models import Question
from sentence_transformers import SentenceTransformer


class Command(BaseCommand):
    help = "Generate AI embeddings for existing questions."

    def handle(self, *args, **options):

        self.stdout.write(
            self.style.WARNING(
                "Loading AI embedding model..."
            )
        )

        model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        self.stdout.write(
            self.style.SUCCESS(
                "AI model loaded successfully."
            )
        )

        questions = Question.objects.filter(
            embedding__isnull=True
        )

        total = questions.count()

        if total == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    "All questions already have embeddings."
                )
            )
            return

        self.stdout.write(
            f"Questions requiring embeddings: {total}"
        )

        completed = 0

        for question in questions:

            try:
                embedding = model.encode(
                    question.question_text
                ).tolist()

                question.embedding = embedding
                question.save(
                    update_fields=["embedding"]
                )

                completed += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"[{completed}/{total}] "
                        f"Embedding generated for Question "
                        f"{question.id}"
                    )
                )

            except Exception as e:

                self.stdout.write(
                    self.style.ERROR(
                        f"Failed for Question "
                        f"{question.id}: {e}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nCompleted: {completed}/{total} questions."
            )
        )