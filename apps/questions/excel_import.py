import pandas as pd

from .embedding_service import generate_embedding
from .ai_service import classify_question
from .models import Question


# ---------------------------------------
# Bloom Level Mapping
# ---------------------------------------

BLOOM_MAP = {
    "remember": "1",
    "understand": "2",
    "apply": "3",
    "analyze": "4",
    "evaluate": "5",
    "create": "6",
}


# ---------------------------------------
# Question Type Mapping
# ---------------------------------------

QUESTION_TYPE_MAP = {
    "mcq": "mcq",
    "multiple choice": "mcq",
    "multiple choice questions": "mcq",

    "ftq": "ftq",
    "following the questions": "ftq",

    "case study": "casestudy",
    "casestudy": "casestudy",
    "case-study": "casestudy",

    # AI may return "cs"
    "cs": "casestudy",
}


# ---------------------------------------
# Column Aliases
# ---------------------------------------

COLUMN_ALIASES = {

    "question": {
        "question",
        "questions",
        "question text",
        "question_text",
    },

    "module": {
        "module",
        "mod",
    },

    "unit": {
        "unit",
        "chapter",
    },

    "bloom": {
        "bloom",
        "bloom level",
        "blooms level",
        "bloomlevel",
    },

    "mark": {
        "mark",
        "marks",
        "score",
    },

    "difficulty": {
        "difficulty",
        "level",
        "question level",
    },

    "question_type": {
        "question type",
        "question_type",
        "type",
    },

}


# ---------------------------------------
# Normalize Column Name
# ---------------------------------------

def normalize_column_name(column):

    return (
        str(column)
        .strip()
        .lower()
        .replace("_", " ")
    )


# ---------------------------------------
# Find Column
# ---------------------------------------

def find_column(df, field):

    normalized_columns = {
        normalize_column_name(col): col
        for col in df.columns
    }

    for alias in COLUMN_ALIASES[field]:

        alias = normalize_column_name(alias)

        if alias in normalized_columns:
            return normalized_columns[alias]

    return None


# ---------------------------------------
# Excel Importer
# ---------------------------------------

class ExcelImporter:

    def __init__(
        self,
        file_path,
        teacher,
        program,
        semester,
        subject
    ):

        self.file_path = file_path
        self.teacher = teacher
        self.program = program
        self.semester = semester
        self.subject = subject
        self.imported_count = 0

    def import_data(self):

        try:

            # ---------------------------------------
            # Read Excel
            # ---------------------------------------

            df = pd.read_excel(self.file_path)

            df = df.dropna(how="all")

            # ---------------------------------------
            # Required Columns
            # ---------------------------------------

            # AI will generate:
            # - Bloom Level
            # - Difficulty
            # - Question Type
            #
            # Therefore these three columns are
            # no longer required from Excel.

            required_fields = [
                "question",
                "unit",
                "mark",
                "bloom",
                "difficulty",
                "question_type",
            ]

            columns = {
                field: find_column(df, field)
                for field in required_fields
            }

            missing = [
                field
                for field, column in columns.items()
                if column is None
            ]

            if missing:

                missing = [
                    m.replace("_", " ").title()
                    for m in missing
                ]

                return False, [
                    "Missing Required Columns:",
                    *missing
                ]

            self.imported_count = 0

            # ---------------------------------------
            # Process Each Question
            # ---------------------------------------

            for index, row in df.iterrows():

                question_text = str(
                    row[columns["question"]]
                ).strip()

                # Ignore empty rows
                if question_text in ["", "nan", "None"]:
                    continue

                # ---------------------------------------
                # Read Unit
                # ---------------------------------------

                unit = str(
                    row[columns["unit"]]
                ).strip()

                # ---------------------------------------
                # Read Marks
                # ---------------------------------------

                marks_value = pd.to_numeric(
                    row[columns["mark"]],
                    errors="coerce"
                )

                if pd.isna(marks_value):
                    return False, [
                        f"Invalid marks at Excel row {index + 2}."
                    ]

                marks = int(marks_value)

                if marks <= 0:
                    return False, [
                        f"Marks must be greater than 0 at Excel row {index + 2}."
                    ]

                # ---------------------------------------
                # Read Classification from Excel
                # ---------------------------------------

                bloom_raw = str(
                    row[columns["bloom"]]
                ).strip().lower()

                bloom_value = BLOOM_MAP.get(
                    bloom_raw,
                    bloom_raw
                )

                difficulty_value = str(
                    row[columns["difficulty"]]
                ).strip().lower()

                question_type_value = str(
                    row[columns["question_type"]]
                ).strip().lower()

                # ---------------------------------------
                # Normalize AI Question Type
                # ---------------------------------------

                question_type_value = QUESTION_TYPE_MAP.get(
                    question_type_value,
                    question_type_value
                )

                # ---------------------------------------
                # Validate AI Result
                # ---------------------------------------

                if bloom_value not in {
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                }:

                    return False, [
                        f"Invalid Bloom level returned by AI "
                        f"for Excel row {index + 2}: "
                        f"{bloom_value}"
                    ]

                if difficulty_value not in {
                    "easy",
                    "medium",
                    "hard",
                }:

                    return False, [
                        f"Invalid difficulty returned by AI "
                        f"for Excel row {index + 2}: "
                        f"{difficulty_value}"
                    ]

                if question_type_value not in {
                    "mcq",
                    "ftq",
                    "casestudy",
                }:

                    return False, [
                        f"Invalid question type returned by AI "
                        f"for Excel row {index + 2}: "
                        f"{question_type_value}"
                    ]

                # ---------------------------------------
                # Generate AI Embedding
                # ---------------------------------------

                embedding = generate_embedding(
                    question_text
                )

                # ---------------------------------------
                # Create Question
                # ---------------------------------------

                Question.objects.create(

                    teacher=self.teacher,

                    program=self.program,

                    semester=self.semester,

                    subject=self.subject,

                    unit=unit,

                    question_text=question_text,

                    # AI classification
                    bloom_level=bloom_value,

                    difficulty=difficulty_value,

                    question_type=question_type_value,

                    marks=marks,

                    # AI embedding
                    embedding=embedding,
                )

                self.imported_count += 1

            # ---------------------------------------
            # Import Completed
            # ---------------------------------------

            return True, (
                f"{self.imported_count} Questions "
                f"Imported Successfully"
            )

        except Exception as e:

            return False, [str(e)]