from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class Survey(models.Model):
    """Survey model to represent a questionnaire with multiple questions"""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='surveys')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Survey'
        verbose_name_plural = 'Surveys'
    
    def _str_(self):
        return self.title
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('survey_detail', kwargs={'slug': self.slug})
    
    @property
    def response_count(self):
        return SurveyResponse.objects.filter(survey=self).count()
    
    @property
    def question_count(self):
        return self.questions.count()
    
    @property
    def completion_rate(self):
        """Calculate percentage of completed responses vs started responses"""
        total = SurveyResponse.objects.filter(survey=self).count()
        completed = SurveyResponse.objects.filter(survey=self, is_complete=True).count()
        if total == 0:
            return 0
        return (completed / total) * 100


class QuestionType(models.Model):
    """Question type model to define different types of questions"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Define the available question types as constants
    TEXT = 'text'
    SINGLE_CHOICE = 'single_choice'
    MULTIPLE_CHOICE = 'multiple_choice'
    RATING = 'rating'
    DATE = 'date'
    NUMBER = 'number'
    FILE_UPLOAD = 'file_upload'
    
    TYPE_CHOICES = [
        (TEXT, 'Text'),
        (SINGLE_CHOICE, 'Single Choice'),
        (MULTIPLE_CHOICE, 'Multiple Choice'),
        (RATING, 'Rating Scale'),
        (DATE, 'Date'),
        (NUMBER, 'Number'),
        (FILE_UPLOAD, 'File Upload'),
    ]
    
    type_code = models.CharField(max_length=50, choices=TYPE_CHOICES, unique=True)
    
    def _str_(self):
        return self.name


class Question(models.Model):
    """Question model to represent a question in a survey"""
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    question_type = models.ForeignKey(QuestionType, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    description = models.TextField(blank=True)
    is_required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional fields for specific question types
    min_value = models.IntegerField(null=True, blank=True)  # For number and rating questions
    max_value = models.IntegerField(null=True, blank=True)  # For number and rating questions
    allow_multiple = models.BooleanField(default=False)  # For allowing multiple answers
    
    class Meta:
        ordering = ['order']
    
    def _str_(self):
        return f"{self.survey.title} - {self.text[:50]}"
    
    @property
    def response_count(self):
        return QuestionResponse.objects.filter(question=self).count()
    
    @property
    def choice_count(self):
        return self.choices.count() if hasattr(self, 'choices') else 0


class QuestionChoice(models.Model):
    """Model for choices in multiple-choice or single-choice questions"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def _str_(self):
        return self.text
    
    @property
    def response_count(self):
        return QuestionResponse.objects.filter(
            selected_choices=self
        ).count()
    
    @property
    def response_percentage(self):
        total = self.question.response_count
        if total == 0:
            return 0
        return (self.response_count / total) * 100


class SurveyResponse(models.Model):
    """Model to represent a user's response to a survey"""
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    respondent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='survey_responses')
    respondent_ip = models.GenericIPAddressField(null=True, blank=True)
    submission_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_complete = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-started_at']
    
    def _str_(self):
        return f"Response to {self.survey.title} ({self.submission_id})"
    
    @property
    def completion_time(self):
        """Calculate time taken to complete the survey"""
        if self.completed_at and self.started_at:
            return self.completed_at - self.started_at
        return None
    
    @property
    def response_count(self):
        return self.question_responses.count()


class QuestionResponse(models.Model):
    """Model for a response to a specific question"""
    survey_response = models.ForeignKey(SurveyResponse, on_delete=models.CASCADE, related_name='question_responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='responses')
    
    # Different types of responses
    text_response = models.TextField(blank=True, null=True)
    number_response = models.FloatField(blank=True, null=True)
    date_response = models.DateField(blank=True, null=True)
    selected_choices = models.ManyToManyField(QuestionChoice, blank=True, related_name='responses')
    file_response = models.FileField(upload_to='survey_uploads/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def _str_(self):
        return f"Response to {self.question.text[:30]}"
    
    @property
    def response_type(self):
        """Return the type of response based on which field is populated"""
        if self.text_response:
            return 'text'
        elif self.number_response is not None:
            return 'number'
        elif self.date_response:
            return 'date'
        elif self.selected_choices.exists():
            return 'choice'
        elif self.file_response:
            return 'file'
        return None