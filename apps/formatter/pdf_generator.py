from pathlib import Path
from xml.sax.saxutils import escape

from django.conf import settings

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from .paper_formatter import PaperFormatter


class PDFGenerator(PaperFormatter):
    """
    Generate the current GeneratedPaper as a compact
    academic question paper PDF.
    """

    @classmethod
    def generate_paper(cls, paper):
        filename = (
            f"paper_{paper.id}_"
            f"{paper.created_at.strftime('%Y%m%d_%H%M%S')}.pdf"
        )

        pdf_dir = (
            Path(settings.MEDIA_ROOT)
            / "generated_papers"
            / "pdf"
        )

        pdf_dir.mkdir(parents=True, exist_ok=True)

        filepath = str(pdf_dir / filename)

        # -------------------------------------------------
        # PAGE
        # -------------------------------------------------

        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            leftMargin=11 * mm,
            rightMargin=11 * mm,
            topMargin=10 * mm,
            bottomMargin=10 * mm,
            title="Question Paper",
        )

        # -------------------------------------------------
        # STYLES
        # -------------------------------------------------

        normal = ParagraphStyle(
            "NormalPaper",
            fontName="Times-Roman",
            fontSize=10,
            leading=12,
            spaceAfter=0,
            spaceBefore=0,
            alignment=TA_LEFT,
        )

        normal_center = ParagraphStyle(
            "NormalCenter",
            parent=normal,
            alignment=TA_CENTER,
        )

        bold = ParagraphStyle(
            "BoldPaper",
            parent=normal,
            fontName="Times-Bold",
        )

        header_small = ParagraphStyle(
            "HeaderSmall",
            parent=normal,
            fontSize=9.5,
            leading=11,
        )

        college_style = ParagraphStyle(
            "College",
            parent=normal,
            fontName="Times-Bold",
            fontSize=13,
            leading=14,
            alignment=TA_CENTER,
        )

        table_style = ParagraphStyle(
            "Table",
            parent=normal,
            fontSize=9.5,
            leading=11,
        )

        table_center = ParagraphStyle(
            "TableCenter",
            parent=table_style,
            alignment=TA_CENTER,
        )

        table_bold = ParagraphStyle(
            "TableBold",
            parent=table_style,
            fontName="Times-Bold",
        )

        # -------------------------------------------------
        # HELPER
        # -------------------------------------------------

        def safe(value):
            if value is None:
                return ""
            return escape(str(value))

        # -------------------------------------------------
        # HEADER
        # -------------------------------------------------

        program_name = (
            paper.pattern.program.name
            if paper.pattern.program
            else ""
        )

        subject_name = (
            paper.pattern.subject.name
            if paper.pattern.subject
            else ""
        )

        semester_number = (
            paper.pattern.semester.number
            if paper.pattern.semester
            else ""
        )

        exam_date = ""

        if paper.pattern.exam_date:
            exam_date = paper.pattern.exam_date.strftime("%d/%m/%Y")

        exam_type = paper.pattern.get_exam_type_display()

        header = []

        # Top row
        top_row = Table(
            [
                [
                    Paragraph(
                        f"Programme: {safe(program_name)}",
                        header_small,
                    ),
                    Paragraph(
                        "Roll No. __________________",
                        ParagraphStyle(
                            "Roll",
                            parent=header_small,
                            alignment=TA_RIGHT,
                        ),
                    ),
                ]
            ],
            colWidths=[90 * mm, 90 * mm],
        )

        top_row.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ]
            )
        )

        header.append(top_row)

        # College
        header.append(
            Paragraph(
                "VIDYALANKAR SCHOOL OF INFORMATION TECHNOLOGY",
                college_style,
            )
        )

        header.append(Spacer(1, 2))

        # Date / exam / time
        middle_row = Table(
            [
                [
                    Paragraph(
                        f"Date: <b>{safe(exam_date)}</b>",
                        header_small,
                    ),
                    Paragraph(
                        safe(exam_type),
                        ParagraphStyle(
                            "ExamType",
                            parent=header_small,
                            fontName="Times-Bold",
                            alignment=TA_CENTER,
                        ),
                    ),
                    Paragraph(
                        f"Time: <b>{safe(paper.pattern.time_allowed)}</b>",
                        ParagraphStyle(
                            "Time",
                            parent=header_small,
                            fontName="Times-Bold",
                            alignment=TA_RIGHT,
                        ),
                    ),
                ]
            ],
            colWidths=[55 * mm, 80 * mm, 45 * mm],
        )

        middle_row.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 1),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ]
            )
        )

        header.append(middle_row)

        # Course / subject / marks
        bottom_row = Table(
            [
                [
                    Paragraph(
                        f"<b>F. Y. {safe(program_name)}</b>"
                        f"&nbsp;&nbsp;&nbsp;"
                        f"<b>SEM - {safe(semester_number)}</b>",
                        header_small,
                    ),
                    Paragraph(
                        f"<b>Subject: {safe(subject_name)}</b>",
                        ParagraphStyle(
                            "Subject",
                            parent=header_small,
                            alignment=TA_CENTER,
                        ),
                    ),
                    Paragraph(
                        f"<b>Marks: {safe(paper.pattern.total_marks)}</b>",
                        ParagraphStyle(
                            "Marks",
                            parent=header_small,
                            alignment=TA_RIGHT,
                        ),
                    ),
                ]
            ],
            colWidths=[55 * mm, 80 * mm, 45 * mm],
        )

        bottom_row.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 1),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )

        header.append(bottom_row)

        # Header line
        line = Table(
            [[""]],
            colWidths=[180 * mm],
            rowHeights=[1],
        )

        line.setStyle(
            TableStyle(
                [
                    ("LINEBELOW", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )

        header.append(line)
        header.append(Spacer(1, 5))

        # -------------------------------------------------
        # MAIN TABLE
        # -------------------------------------------------

        table_data = []

        # Table header
        table_data.append(
            [
                Paragraph(
                    "Bloom's<br/>Taxonomy<br/>Level",
                    table_bold,
                ),
                Paragraph(
                    "OC",
                    ParagraphStyle(
                        "OCHeader",
                        parent=table_bold,
                        alignment=TA_CENTER,
                    ),
                ),
                Paragraph(
                    "Q.No.",
                    ParagraphStyle(
                        "QNoHeader",
                        parent=table_bold,
                        alignment=TA_CENTER,
                    ),
                ),
                Paragraph(
                    "",
                    table_bold,
                ),
                Paragraph(
                    "Marks",
                    ParagraphStyle(
                        "MarksHeader",
                        parent=table_bold,
                        alignment=TA_CENTER,
                    ),
                ),
            ]
        )

        # -------------------------------------------------
        # GENERATED QUESTIONS
        # -------------------------------------------------

        generated_questions = (
            paper.generated_questions
            .select_related(
                "question",
                "section",
            )
            .order_by(
                "display_order"
            )
        )

        generated_by_section = {}

        for generated in generated_questions:
            generated_by_section.setdefault(
                generated.section_id,
                []
            ).append(generated)

        sections = (
            paper.pattern.sections
            .all()
            .order_by("display_order")
        )

        for section in sections:

            # ---------------------------------------------
            # SECTION HEADER
            # ---------------------------------------------

            attempt_text = (
                section.custom_attempt_text
                if section.attempt_rule == "custom"
                else section.get_attempt_rule_display()
            )

            question_type_text = (
                section.get_question_type_display_name()
                if section.question_type
                else ""
            )

            section_title = safe(attempt_text)

            if question_type_text:
                section_title += (
                    " - "
                    + safe(question_type_text)
                )

            table_data.append(
                [
                    "",
                    "",
                    Paragraph(
                        f"<b>{safe(section.question_number)}</b>",
                        table_center,
                    ),
                    Paragraph(
                        f"<b>{section_title}</b>",
                        table_bold,
                    ),
                    Paragraph(
                        f"<b>{safe(section.marks)}</b>",
                        table_center,
                    ),
                ]
            )

            # ---------------------------------------------
            # QUESTIONS IN SECTION
            # ---------------------------------------------

            section_questions = generated_by_section.get(
                section.id,
                []
            )

            for index, generated in enumerate(
                section_questions
            ):

                question = generated.question

                # Bloom label
                bloom_label = (
                    question.get_bloom_level_display()
                    if question.bloom_level
                    else ""
                )

                # CO
                co = ""

                # Current Question model does not have CO.
                # PatternQuestionSetting contains CO.
                try:
                    setting = (
                        section.question_settings
                        .all()
                        .order_by("slot_number")
                    )[index]

                    co = setting.co or ""

                except Exception:
                    co = section.co or ""

                # Letter
                letter = chr(
                    ord("a") + index
                )

                table_data.append(
                    [
                        Paragraph(
                            safe(bloom_label),
                            table_center,
                        ),
                        Paragraph(
                            safe(co),
                            table_center,
                        ),
                        Paragraph(
                            f"<b>{letter}</b>",
                            table_center,
                        ),
                        Paragraph(
                            safe(question.question_text)
                            .replace("\n", "<br/>"),
                            table_style,
                        ),
                        "",
                    ]
                )

        # -------------------------------------------------
        # TABLE
        # -------------------------------------------------

        exam_table = Table(
            table_data,
            colWidths=[
                25 * mm,
                13 * mm,
                21 * mm,
                110 * mm,
                11 * mm,
            ],
            repeatRows=1,
            hAlign="CENTER",
        )

        exam_table.setStyle(
            TableStyle(
                [
                    # Borders
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.6,
                        colors.HexColor("#777777"),
                    ),

                    # Alignment
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),

                    # Header
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, 0),
                        "MIDDLE",
                    ),

                    # Compact padding
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        4,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        4,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        2,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        2,
                    ),

                    # Section header
                    (
                        "VALIGN",
                        (0, 1),
                        (-1, -1),
                        "TOP",
                    ),
                ]
            )
        )

        # -------------------------------------------------
        # BUILD
        # -------------------------------------------------

        story = []

        story.extend(header)

        story.append(exam_table)

        doc.build(story)

        return (
            f"generated_papers/pdf/{filename}"
        )