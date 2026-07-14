from rest_framework import serializers
from .models import PaperPattern, GeneratedPaper
from apps.questions.serializers import QuestionSerializer
class PaperPatternSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaperPattern
        fields = '__all__'
        read_only_fields = ['teacher']
class GeneratedPaperSerializer(serializers.ModelSerializer):
    pattern_name = serializers.CharField(source='pattern.name', read_only=True)
    section_a_questions = QuestionSerializer(many=True, read_only=True)
    section_b_questions = QuestionSerializer(many=True, read_only=True)
    section_c_questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = GeneratedPaper
        fields = '__all__'
        read_only_fields = ['teacher']