from apps.questions.models import Question
from apps.questions.question_selection_service import select_best_question
from apps.questions.embedding_service import generate_embedding


class PaperGeneratorService:

    def __init__(self, pattern, teacher):

        self.pattern = pattern
        self.teacher = teacher

        # Questions already selected anywhere
        # in this generated paper.
        self.used_question_ids = set()

    # =========================================================
    # CREATE REFERENCE TEXT FOR A PATTERN SLOT
    # =========================================================

    def create_reference_text(self, section, setting):

        subject_name = self.pattern.subject.name

        unit_text = (
            f"Unit {setting.unit}"
            if setting.unit
            else "All Units"
        )

        bloom_text = (
            f"Bloom level {setting.bloom_level}"
            if setting.bloom_level
            else ""
        )

        difficulty_text = (
            f"{setting.difficulty} difficulty"
            if setting.difficulty
            else ""
        )

        question_type_text = (
            f"{section.question_type} question"
            if section.question_type
            else ""
        )

        reference_text = (
            f"Subject: {subject_name}. "
            f"{unit_text}. "
            f"{bloom_text}. "
            f"{difficulty_text}. "
            f"{question_type_text}."
        )

        return reference_text

    # =========================================================
    # CREATE REFERENCE EMBEDDING
    # =========================================================

    def create_reference_embedding(self, section, setting):

        reference_text = self.create_reference_text(
            section,
            setting
        )

        return generate_embedding(reference_text)

    # =========================================================
    # GET ELIGIBLE QUESTIONS
    # =========================================================

    def get_eligible_questions(self, section, setting):

        queryset = Question.objects.filter(

            teacher=self.teacher,

            is_active=True,

            program=self.pattern.program,

            semester=self.pattern.semester,

            subject=self.pattern.subject,

            # SAME MARKS
            marks=section.marks,

            # SAME DIFFICULTY
            difficulty__iexact=setting.difficulty,
            
            
            # SAME QUESTION TYPE
            question_type__iexact=section.question_type,

            # SAME BLOOM LEVEL
            bloom_level__iexact=setting.bloom_level,
            
        )

        # =====================================================
        # INDIVIDUAL QUESTION UNIT
        # =====================================================

        if setting.unit:

            queryset = queryset.filter(
                unit__iexact=str(setting.unit)
            )

        # =====================================================
        # PREVENT DUPLICATES
        # =====================================================

        if self.used_question_ids:

            queryset = queryset.exclude(
                id__in=self.used_question_ids
            )

        return list(queryset)

    # =========================================================
    # GENERATE ONE SECTION
    # =========================================================

    def generate_section(self, section):

        generated_questions = []

        settings = list(
            section.question_settings.all()
            .order_by("slot_number")
        )

        required_count = (
            section.number_of_questions
        )

        # =====================================================
        # VALIDATE SETTINGS
        # =====================================================

        if len(settings) < required_count:

            raise ValueError(
                f"{section.question_number} has only "
                f"{len(settings)} question settings, "
                f"but requires {required_count}."
            )

        # =====================================================
        # GENERATE EACH QUESTION
        # =====================================================

        for index in range(required_count):

            setting = settings[index]

            available_questions = (
                self.get_eligible_questions(
                    section,
                    setting
                )
            )

            # =================================================
            # NO QUESTION FOUND
            # =================================================

            if not available_questions:

                unit_display = (
                    f"Unit {setting.unit}"
                    if setting.unit
                    else "All Units"
                )

                raise ValueError(
                    f"Cannot generate {section.question_number}, "
                    f"Question {setting.slot_number}. "
                    f"No eligible question exists with "
                    f"Marks={section.marks}, "
                    f"Difficulty={setting.difficulty}, "
                    f"Unit={unit_display}, "
                    f"Bloom={setting.bloom_level}, "
                    f"Type={section.question_type}. "
                    f"Please add a matching question or change "
                    f"the pattern requirement."
                )

            # =================================================
            # CREATE REFERENCE EMBEDDING
            # =================================================

            try:

                reference_embedding = (
                    self.create_reference_embedding(
                        section,
                        setting
                    )
                )

            except Exception as e:

                raise ValueError(
                    f"Unable to create semantic reference "
                    f"for {section.question_number}, "
                    f"Question {setting.slot_number}: {e}"
                )

            # =================================================
            # AI-ASSISTED QUESTION SELECTION
            # =================================================

            selection = select_best_question(

                questions=available_questions,

                required_bloom_level=(
                    setting.bloom_level
                ),

                required_question_type=(
                    section.question_type
                ),

                reference_question=None,

                reference_embedding=(
                    reference_embedding
                ),
            )

            # =================================================
            # AI SELECTION FAILED
            # =================================================

            if not selection:

                raise ValueError(

                    f"Unable to select a question for "
                    f"{section.question_number}, "
                    f"Question {setting.slot_number}."
                )

            selected_question = (
                selection["question"]
            )

            # =================================================
            # SAVE SELECTED QUESTION
            # =================================================

            generated_questions.append(
                selected_question
            )

            # =================================================
            # MARK AS USED
            # =================================================

            self.used_question_ids.add(
                selected_question.id
            )

        return generated_questions

    # =========================================================
    # GENERATE COMPLETE PAPER
    # =========================================================

    def generate_questions(self):

        generated_data = []

        sections = (
            self.pattern.sections
            .prefetch_related(
                "question_settings"
            )
            .order_by(
                "display_order"
            )
        )

        for section in sections:

            questions = (
                self.generate_section(
                    section
                )
            )

            generated_data.append({

                "section": section,

                "questions": questions,

            })

        return generated_data

    # =========================================================
    # VALIDATE QUESTION BANK
    # =========================================================

    def validate_question_bank(self):
    
        validation_results = []

        sections = (
            self.pattern.sections
            .prefetch_related("question_settings")
            .order_by("display_order")
        )

        all_slots_valid = True

        for section in sections:

            settings = list(
                section.question_settings.all()
                .order_by("slot_number")
            )

            required_count = section.number_of_questions

            # ---------------------------------------------
        # Check missing settings
        # ---------------------------------------------

            if len(settings) < required_count:

                all_slots_valid = False

                validation_results.append({
                    "section": section.question_number,
                    "slot": None,
                    "valid": False,
                    "available": 0,
                    "required": 1,
                   "message": (
                        f"{section.question_number} has only "
                        f"{len(settings)} question settings, "
                        f"but requires {required_count}."
                    ),
                })

                continue

        # ---------------------------------------------
        # Check every slot
        # ---------------------------------------------

            for setting in settings[:required_count]:

                eligible_questions = (
                    self.get_eligible_questions(
                        section,
                        setting
                    )
                )

                available_count = len(eligible_questions)

                is_valid = available_count > 0

                if not is_valid:
                    all_slots_valid = False

                unit_display = (
                    f"Unit {setting.unit}"
                    if setting.unit
                    else "All Units"
                )

                validation_results.append({
                    "section": section.question_number,
                    "slot": setting.slot_number,
                    "valid": is_valid,
                    "available": available_count,
                    "required": 1,
                    "unit": setting.unit,
                    "marks": section.marks,
                    "difficulty": setting.difficulty,
                    "bloom_level": setting.bloom_level,
                    "question_type": section.question_type,
                    "message": (
                        f"{available_count} eligible question(s) "
                        f"available for "
                        f"{section.question_number}, "
                        f"Question {setting.slot_number}. "
                        f"Requirement: "
                        f"{section.marks} marks, "
                        f"{setting.difficulty}, "
                        f"{unit_display}, "
                        f"Bloom {setting.bloom_level}, "
                        f"{section.question_type}."
                    ),
                })

        return {
            "sufficient_questions": all_slots_valid,
            "details": validation_results,
        }