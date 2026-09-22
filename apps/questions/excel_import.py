import pandas as pd

from .embedding_service import generate_embeddings_batch
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
            # Store Validated Questions
            # ---------------------------------------

            question_records = []
            question_texts = []

            # ---------------------------------------
            # Process and Validate Questions
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
                        f"Marks must be greater than 0 "
                        f"at Excel row {index + 2}."
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
                # Normalize Question Type
                # ---------------------------------------

                question_type_value = QUESTION_TYPE_MAP.get(
                    question_type_value,
                    question_type_value
                )

                # ---------------------------------------
                # Validate Bloom Level
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
                        f"Invalid Bloom level "
                        f"for Excel row {index + 2}: "
                        f"{bloom_value}"
                    ]

                # ---------------------------------------
                # Validate Difficulty
                # ---------------------------------------

                if difficulty_value not in {
                    "easy",
                    "medium",
                    "hard",
                }:

                    return False, [
                        f"Invalid difficulty "
                        f"for Excel row {index + 2}: "
                        f"{difficulty_value}"
                    ]

                # ---------------------------------------
                # Validate Question Type
                # ---------------------------------------

                if question_type_value not in {
                    "mcq",
                    "ftq",
                    "casestudy",
                }:

                    return False, [
                        f"Invalid question type "
                        f"for Excel row {index + 2}: "
                        f"{question_type_value}"
                    ]

                # ---------------------------------------
                # Store Question Data
                # ---------------------------------------

                question_records.append({
                    "unit": unit,
                    "question_text": question_text,
                    "bloom_level": bloom_value,
                    "difficulty": difficulty_value,
                    "question_type": question_type_value,
                    "marks": marks,
                })

                question_texts.append(question_text)

            # ---------------------------------------
            # Generate All Embeddings in One Batch
            # ---------------------------------------

            embeddings = generate_embeddings_batch(
                question_texts
            )

            # ---------------------------------------
            # Create Questions
            # ---------------------------------------

            for record, embedding in zip(
                question_records,
                embeddings
            ):

                Question.objects.create(

                    teacher=self.teacher,

                    program=self.program,

                    semester=self.semester,

                    subject=self.subject,

                    unit=record["unit"],

                    question_text=record["question_text"],

                    bloom_level=record["bloom_level"],

                    difficulty=record["difficulty"],

                    question_type=record["question_type"],

                    marks=record["marks"],

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