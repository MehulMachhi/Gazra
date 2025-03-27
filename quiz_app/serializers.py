from rest_framework import serializers
from .models import Survey, Question, QuestionChoice, SurveyResponse, QuestionResponse, QuestionType


class QuestionChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionChoice
        fields = ['id', 'text', 'order', 'response_count', 'response_percentage']


class QuestionSerializer(serializers.ModelSerializer):
    choices = QuestionChoiceSerializer(many=True, read_only=True)
    response_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'description', 'is_required', 'order', 'response_count', 'choices']


class SurveySerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    response_count = serializers.IntegerField(read_only=True)
    question_count = serializers.IntegerField(read_only=True)
    completion_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = Survey
        fields = ['id', 'title', 'description', 'slug', 'is_active', 'start_date', 'end_date', 
                  'response_count', 'question_count', 'completion_rate', 'questions']


class SurveyResponseSerializer(serializers.ModelSerializer):
    question_responses = serializers.SerializerMethodField()

    class Meta:
        model = SurveyResponse
        fields = ['id', 'survey', 'respondent', 'submission_id', 'started_at', 'completed_at', 
                  'is_complete', 'completion_time', 'question_responses']

    def get_question_responses(self, obj):
        question_responses = obj.question_responses.all()
        return QuestionResponseSerializer(question_responses, many=True).data


class QuestionResponseSerializer(serializers.ModelSerializer):
    selected_choices = QuestionChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = QuestionResponse
        fields = ['id', 'survey_response', 'question', 'text_response', 'number_response', 
                  'date_response', 'selected_choices', 'file_response', 'created_at', 'response_type']


class QuestionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionType
        fields = ['id', 'name', 'description', 'type_code']
