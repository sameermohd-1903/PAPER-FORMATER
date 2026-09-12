import random

from apps.questions.models import Question


class PaperGeneratorService:

    def __init__(self, pattern, teacher):

        self.pattern = pattern
        self.teacher = teacher

        # Questions already selected anywhere
        # in this generated paper.
        self.used_question_ids = set()


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

                    f"Not enough eligible questions for "
                    f"{section.question_number}, "
                    f"Question {setting.slot_number}. "

                    f"Marks={section.marks}, "

                    f"Difficulty={setting.difficulty}, "

                    f"Bloom={setting.bloom_level}, "

                    f"Type={section.question_type}, "

                    f"Unit={unit_display}."
                )


            # =================================================
            # RANDOM SELECTION
            # =================================================

            selected_question = random.choice(
                available_questions
            )


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

        total_required = sum(

            section.number_of_questions

            for section
            in self.pattern.sections.all()

        )


        total_available = (
            Question.objects.filter(

                teacher=self.teacher,

                is_active=True,

                program=self.pattern.program,

                semester=self.pattern.semester,

                subject=self.pattern.subject,

            ).count()
        )


        return {

            "sufficient_questions":
                total_available >= total_required,

            "details": {

                "total_required":
                    total_required,

                "total_available":
                    total_available,

            }

        }