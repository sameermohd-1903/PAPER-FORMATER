from typing import List
from apps.questions.models import Question
class PaperFormatter:
    """Base class for paper formatting"""
    
    def __init__(self, paper):
        self.paper = paper
        self.college_name = paper.college_name
        self.subject = paper.subject
        self.time_allowed = paper.time_allowed
        self.maximum_marks = paper.maximum_marks
        self.exam_date = paper.exam_date
        
    def format_header(self):
        """Format paper header"""
        header = f"""
        {self.college_name.upper()}
        
        Subject: {self.subject}
        
        Time: {self.time_allowed}
        Maximum Marks: {self.maximum_marks}
        
        """
        return header.strip()
    
    def format_section(self, section_name: str, questions: List[Question], marks_per_question: int):
        """Format a section with questions"""
        section_text = f"\n{section_name.upper()}\n\n"
        
        for i, question in enumerate(questions, 1):
            section_text += f"Q{i}.\n{question.question_text}\n[Marks: {marks_per_question}]\n\n"
        
        return section_text
    
    def format_paper_content(self):
        """Format complete paper content"""
        content = self.format_header()
        
        # Section A
        section_a_questions = list(self.paper.section_a_questions.all())
        if section_a_questions:
            content += self.format_section("SECTION A", section_a_questions, self.paper.pattern.section_a_marks)
        
        # Section B
        section_b_questions = list(self.paper.section_b_questions.all())
        if section_b_questions:
            content += self.format_section("SECTION B", section_b_questions, self.paper.pattern.section_b_marks)
        
        # Section C
        section_c_questions = list(self.paper.section_c_questions.all())
        if section_c_questions:
            content += self.format_section("SECTION C", section_c_questions, self.paper.pattern.section_c_marks)
        
        return content