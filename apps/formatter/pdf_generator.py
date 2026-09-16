from pathlib import Path

from django.conf import settings

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)


class PDFGenerator:
    """
    Generate the final question paper PDF
    from the current PaperPattern structure.
    """

    @classmethod
    def generate_pattern_pdf(cls, pattern, context):

        filename = (
            f"paper_{pattern.id}.pdf"
        )

        pdf_dir = (
            Path(settings.MEDIA_ROOT)
            / "generated_papers"
            / "pdf"
        )

        pdf_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        filepath = pdf_dir / filename

        # --------------------------------------------------
        # DOCUMENT
        # --------------------------------------------------

        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,

            rightMargin=11 * mm,
            leftMargin=11 * mm,

            topMargin=15 * mm,
            bottomMargin=10 * mm,

            title=pattern.pattern_name,
        )

        # --------------------------------------------------
        # STYLES
        # --------------------------------------------------

        styles = getSampleStyleSheet()

        normal = ParagraphStyle(
            "NormalPaper",
            parent=styles["Normal"],
            fontName="Times-Roman",
            fontSize=9.5,
            leading=11,
            spaceBefore=0,
            spaceAfter=0,
            alignment=TA_LEFT,
        )

        center = ParagraphStyle(
            "CenterPaper",
            parent=normal,
            alignment=TA_CENTER,
        )

        bold_center = ParagraphStyle(
            "BoldCenter",
            parent=center,
            fontName="Times-Bold",
        )

        bold_left = ParagraphStyle(
            "BoldLeft",
            parent=normal,
            fontName="Times-Bold",
        )

        college_style = ParagraphStyle(
            "College",
            parent=normal,
            fontName="Times-Bold",
            fontSize=13,
            leading=14,
            alignment=TA_CENTER,
        )

        # --------------------------------------------------
        # STORY
        # --------------------------------------------------

        story = []

        # --------------------------------------------------
        # HEADER
        # --------------------------------------------------

        program_name = (
            pattern.program.name
            if pattern.program
            else ""
        )

        semester_number = (
            pattern.semester.number
            if pattern.semester
            else ""
        )

        subject_name = (
            pattern.subject.name
            if pattern.subject
            else ""
        )

        exam_type = (
            pattern.get_exam_type_display()
        )

        # Row 1
        header_row_1 = [
            Paragraph(
                f"Programme: {program_name}",
                normal
            ),
            Paragraph(
                "Roll No. __________________",
                normal
            ),
        ]

        header_table_1 = Table(
            [header_row_1],
            colWidths=[
                95 * mm,
                95 * mm,
            ],
        )

        header_table_1.setStyle(
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

        story.append(header_table_1)

        # College
        story.append(
            Paragraph(
                "VIDYALANKAR SCHOOL OF INFORMATION TECHNOLOGY",
                college_style,
            )
        )

        story.append(Spacer(1, 2))

        # Row 2
        header_row_2 = [
            Paragraph(
                f"Date: <b>{pattern.exam_date.strftime('%d/%m/%Y')}</b>",
                normal,
            ),
            Paragraph(
                f"<b>{exam_type}</b>",
                center,
            ),
            Paragraph(
                f"<b>Time: {pattern.time_allowed}</b>",
                center,
            ),
        ]

        header_table_2 = Table(
            [header_row_2],
            colWidths=[
                63 * mm,
                64 * mm,
                63 * mm,
            ],
        )

        header_table_2.setStyle(
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

        story.append(header_table_2)

        # Row 3
        header_row_3 = [
            Paragraph(
                f"F. Y. {program_name} &nbsp;&nbsp; SEM - {semester_number}",
                bold_left,
            ),
            Paragraph(
                f"<b>Subject: {subject_name}</b>",
                center,
            ),
            Paragraph(
                f"<b>Marks: {pattern.total_marks}</b>",
                center,
            ),
        ]

        header_table_3 = Table(
            [header_row_3],
            colWidths=[
                63 * mm,
                64 * mm,
                63 * mm,
            ],
        )

        header_table_3.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )

        story.append(header_table_3)

        # Header line
        line_table = Table(
            [[""]],
            colWidths=[190 * mm],
            rowHeights=[1 * mm],
        )

        line_table.setStyle(
            TableStyle(
                [
                    (
                        "LINEBELOW",
                        (0, 0),
                        (-1, -1),
                        1,
                        colors.black,
                    ),
                ]
            )
        )

        story.append(line_table)

        story.append(Spacer(1, 4))

        # --------------------------------------------------
        # MAIN TABLE
        # --------------------------------------------------

        table_data = []

        # Header
        table_data.append(
            [
                Paragraph(
                    "<b>Bloom's<br/>Taxonomy<br/>Level</b>",
                    normal,
                ),
                Paragraph(
                    "<b>OC</b>",
                    bold_center,
                ),
                Paragraph(
                    "<b>Q.No.</b>",
                    bold_center,
                ),
                Paragraph(
                    "",
                    normal,
                ),
                Paragraph(
                    "<b>Marks</b>",
                    bold_center,
                ),
            ]
        )

        sections = context.get(
            "sections",
            []
        )

        for row in sections:

            # ---------------------------------------------
            # SECTION HEADER
            # ---------------------------------------------

            attempt_text = ""

            if getattr(
                row,
                "attempt_rule",
                ""
            ) == "custom":

                attempt_text = (
                    row.custom_attempt_text
                )

            else:

                attempt_text = (
                    row.get_attempt_rule_display()
                )

            question_type_text = ""

            if row.question_type:

                try:
                    question_type_text = (
                        row.get_question_type_display_name()
                    )
                except Exception:
                    question_type_text = (
                        row.question_type
                    )

            section_title = (
                f"{attempt_text}"
            )

            if question_type_text:

                section_title += (
                    f" - {question_type_text}"
                )

            table_data.append(
                [
                    Paragraph("", normal),
                    Paragraph("", normal),

                    Paragraph(
                        f"<b>{row.question_number}</b>",
                        bold_center,
                    ),

                    Paragraph(
                        f"<b>{section_title}</b>",
                        bold_left,
                    ),

                    Paragraph(
                        f"<b>{row.marks}</b>",
                        bold_center,
                    ),
                ]
            )

            # ---------------------------------------------
            # QUESTIONS
            # ---------------------------------------------

            for sp in row.subparts_data:

                question = sp.get(
                    "question"
                )

                if question:

                    bloom = (
                        question.get_bloom_level_display()
                    )

                    question_text = (
                        question.question_text
                    )

                else:

                    bloom = (
                        getattr(
                            row,
                            "bloom_level",
                            ""
                        )
                    )

                    question_text = ""

                co = sp.get(
                    "co",
                    getattr(row, "co", "")
                )

                letter = sp.get(
                    "letter",
                    ""
                )

                table_data.append(
                    [
                        Paragraph(
                            str(bloom),
                            center,
                        ),

                        Paragraph(
                            str(co),
                            center,
                        ),

                        Paragraph(
                            f"<b>{letter}</b>",
                            center,
                        ),

                        Paragraph(
                            question_text,
                            normal,
                        ),

                        Paragraph(
                            "",
                            center,
                        ),
                    ]
                )

        # --------------------------------------------------
        # TABLE
        # --------------------------------------------------

        main_table = Table(
            table_data,

            colWidths=[
                20 * mm,
                10 * mm,
                15 * mm,
                133 * mm,
                12 * mm,
            ],

            repeatRows=1,

            splitByRow=1,
        )

        # --------------------------------------------------
        # TABLE STYLE
        # --------------------------------------------------

        style_commands = [

            # Borders
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey,
            ),

            # Vertical alignment
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

            (
                "ALIGN",
                (1, 0),
                (2, -1),
                "CENTER",
            ),

            (
                "ALIGN",
                (4, 0),
                (4, -1),
                "CENTER",
            ),

            # Compact padding
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                3,
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                3,
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
        ]

        # Make section headers bold / compact
        data_index = 1

        for row in sections:

            style_commands.extend(
                [
                    (
                        "BACKGROUND",
                        (0, data_index),
                        (-1, data_index),
                        colors.white,
                    ),

                    (
                        "VALIGN",
                        (0, data_index),
                        (-1, data_index),
                        "MIDDLE",
                    ),

                    (
                        "TOPPADDING",
                        (0, data_index),
                        (-1, data_index),
                        2,
                    ),

                    (
                        "BOTTOMPADDING",
                        (0, data_index),
                        (-1, data_index),
                        2,
                    ),
                ]
            )

            data_index += 1

            data_index += len(
                row.subparts_data
            )

        main_table.setStyle(
            TableStyle(style_commands)
        )

        story.append(main_table)

        # --------------------------------------------------
        # BUILD PDF
        # --------------------------------------------------

        doc.build(story)

        return str(
            Path("generated_papers")
            / "pdf"
            / filename
        )