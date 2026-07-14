import pandas as pd

from .models import Question


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

            df = pd.read_excel(self.file_path)

            df = df.dropna(how="all")

            required_fields = [

                "question",

                "module",

                "unit",

                "bloom",

                "mark",

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

            for _, row in df.iterrows():

                question_text = str(

                    row[columns["question"]]

                ).strip()

                if question_text in ["", "nan", "None"]:

                    continue

                # Read Module (for future use)
                module = str(

                    row[columns["module"]]

                ).strip()

                Question.objects.create(

                    teacher=self.teacher,

                    program=self.program,

                    semester=self.semester,

                    subject=self.subject,

                    unit=str(

                        row[columns["unit"]]

                    ).strip(),

                    question_text=question_text,

                    bloom_level=str(

                        row[columns["bloom"]]

                    ).strip().lower(),

                    difficulty=str(

                        row[columns["difficulty"]]

                    ).strip().lower(),

                    question_type=str(

                        row[columns["question_type"]]

                    ).strip().lower(),

                    marks=int(

                        pd.to_numeric(

                            row[columns["mark"]],

                            errors="coerce"

                        ) or 0

                    )

                )

                self.imported_count += 1

            return True, (

                f"{self.imported_count} Questions Imported Successfully"

            )

        except Exception as e:

            return False, [str(e)]