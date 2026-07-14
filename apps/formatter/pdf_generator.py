from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from pathlib import Path
from django.conf import settings
from .paper_formatter import PaperFormatter
class PDFGenerator(PaperFormatter):
    """PDF generation using ReportLab"""
    
    @classmethod
    def generate_paper(cls, paper):
        """Generate PDF file for the paper"""
        # Create filename
        filename = f"paper_{paper.id}_{paper.created_at.strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_dir = Path(settings.MEDIA_ROOT) / 'generated_papers' / 'pdf'
        pdf_dir.mkdir(parents=True, exist_ok=True)
        filepath = str(pdf_dir / filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            topMargin=1*inch,
            bottomMargin=1*inch,
            leftMargin=1*inch,
            rightMargin=1*inch
        )
        
        # Create styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center
        )
        section_style = ParagraphStyle(
            'CustomSection',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20
        )
        question_style = ParagraphStyle(
            'CustomQuestion',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=6,
            leftIndent=20
        )
        
        # Build content
        story = []
        
        # Header
        header_text = f"""
        <b>{paper.college_name.upper()}</b><br/><br/>
        <b>Subject: {paper.subject}</b><br/><br/>
        <b>Time: {paper.time_allowed}</b><br/>
        <b>Maximum Marks: {paper.maximum_marks}</b><br/><br/>
        """
        story.append(Paragraph(header_text, title_style))
        story.append(Spacer(1, 20))
        
        # Sections
        # Section A
        section_a_questions = list(paper.section_a_questions.all())
        if section_a_questions:
            story.append(Paragraph("<b>SECTION A</b>", section_style))
            for i, question in enumerate(section_a_questions, 1):
                q_text = f"<b>Q{i}.</b> {question.question_text} <i>[Marks: {paper.pattern.section_a_marks}]</i>"
                story.append(Paragraph(q_text, question_style))
                story.append(Spacer(1, 10))
        
        # Section B
        section_b_questions = list(paper.section_b_questions.all())
        if section_b_questions:
            story.append(Paragraph("<b>SECTION B</b>", section_style))
            for i, question in enumerate(section_b_questions, 1):
                q_text = f"<b>Q{i}.</b> {question.question_text} <i>[Marks: {paper.pattern.section_b_marks}]</i>"
                story.append(Paragraph(q_text, question_style))
                story.append(Spacer(1, 10))
        
        # Section C
        section_c_questions = list(paper.section_c_questions.all())
        if section_c_questions:
            story.append(Paragraph("<b>SECTION C</b>", section_style))
            for i, question in enumerate(section_c_questions, 1):
                q_text = f"<b>Q{i}.</b> {question.question_text} <i>[Marks: {paper.pattern.section_c_marks}]</i>"
                story.append(Paragraph(q_text, question_style))
                story.append(Spacer(1, 10))
        
        # Generate PDF
        doc.build(story)
        
        return f"generated_papers/pdf/{filename}"