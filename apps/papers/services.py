import random
from typing import List, Dict, Tuple
from django.db.models import Q
from apps.questions.models import Question
from .models import PaperPattern, PatternSection


class QuestionGenerator:
    
    def __init__(self, pattern):
        self.pattern = pattern
        self.selected_questions = set()

    def generate(self):
        """
        Generate a complete paper based on the pattern.
        """

        generated_paper.append({
            "section": section,
            "questions": questions,
            "total_questions": len(questions),
        })

        return generated_paper

    def generate_section(self, section):
        """
        Generate random questions for one PatternSection.
        """

        queryset = Question.objects.filter(
            teacher=self.pattern.teacher,
            program=self.pattern.program,
            semester=self.pattern.semester,
            subject=self.pattern.subject,
            unit=section.unit,
            bloom=section.bloom_level,
            difficulty=section.difficulty,
            question_type=section.question_type,
            marks=section.marks,
        ).exclude(
            id__in=self.selected_questions
        )

        available_questions = list(queryset)

        if len(available_questions) < section.number_of_questions:
            raise ValueError(
                f"Not enough questions for {section.question_number}"
            )

        selected = random.sample(
            available_questions,
            section.number_of_questions
        )

        self.selected_questions.update(
            question.id for question in selected
        )

        return selected


class PaperGeneratorService:
    """Service class for generating question papers"""
    
    def __init__(self, pattern: PaperPattern, teacher):
        self.pattern = pattern
        self.teacher = teacher
        self.used_question_ids = set()
    
    def get_available_questions(self, difficulty: str) -> List[Question]:
        """Get available questions matching criteria"""
        return list(Question.objects.filter(
            teacher=self.teacher,
            subject=self.pattern.subject,
            difficulty=difficulty
        ).exclude(id__in=self.used_question_ids))
    
    def calculate_difficulty_distribution(self, total_questions: int) -> Dict[str, int]:
        """Calculate number of questions per difficulty level"""
        return {
            'easy': int(total_questions * self.pattern.easy_percentage / 100),
            'medium': int(total_questions * self.pattern.medium_percentage / 100),
            'hard': int(total_questions * self.pattern.hard_percentage / 100),
            'long_answer': int(total_questions * self.pattern.long_answer_percentage / 100),
        }
    
    def select_questions_for_section(self, section_count: int, section_marks: int) -> List[Question]:
        """Select questions for a section"""
        selected_questions = []
        
        # Calculate difficulty distribution for this section
        dist = self.calculate_difficulty_distribution(section_count)
        
        # Select questions for each difficulty level
        for difficulty, count in dist.items():
            if count == 0:
                continue
                
            available = self.get_available_questions(difficulty)
            
            if len(available) < count:
                # If not enough questions of this difficulty, use all available
                selected = available
            else:
                selected = random.sample(available, count)
                
            selected_questions.extend(selected)
            self.used_question_ids.update(q.id for q in selected)
        
        # If we still need more questions, fill with any available
        remaining = section_count - len(selected_questions)
        if remaining > 0:
            available = list(Question.objects.filter(
                teacher=self.teacher,
                subject=self.pattern.subject
            ).exclude(id__in=self.used_question_ids))
            
            if available:
                additional = random.sample(available, min(remaining, len(available)))
                selected_questions.extend(additional)
                self.used_question_ids.update(q.id for q in additional)
        
        return selected_questions[:section_count]  # Ensure we don't exceed count
    
    def generate_paper(self) -> Tuple[List[Question], List[Question], List[Question]]:
        """Generate paper with questions for all sections"""
        try:
            # Reset used questions
            self.used_question_ids = set()
            
            # Generate section A
            section_a_questions = []
            if self.pattern.section_a_count > 0:
                section_a_questions = self.select_questions_for_section(
                    self.pattern.section_a_count, self.pattern.section_a_marks
                )
            
            # Generate section B
            section_b_questions = []
            if self.pattern.section_b_count > 0:
                section_b_questions = self.select_questions_for_section(
                    self.pattern.section_b_count, self.pattern.section_b_marks
                )
            
            # Generate section C
            section_c_questions = []
            if self.pattern.section_c_count > 0:
                section_c_questions = self.select_questions_for_section(
                    self.pattern.section_c_count, self.pattern.section_c_marks
                )
            
            return section_a_questions, section_b_questions, section_c_questions
            
        except Exception as e:
            raise Exception(f"Error generating paper: {str(e)}")
    
    def validate_question_bank(self) -> Dict[str, bool]:
        """Validate if question bank has sufficient questions"""
        validation = {
            'sufficient_questions': True,
            'details': {}
        }
        
        total_required = (
            self.pattern.section_a_count + 
            self.pattern.section_b_count + 
            self.pattern.section_c_count
        )
        
        total_available = Question.objects.filter(
            teacher=self.teacher,
            subject=self.pattern.subject
        ).count()
        
        validation['details']['total_required'] = total_required
        validation['details']['total_available'] = total_available
        validation['sufficient_questions'] = total_available >= total_required
        
        return validation