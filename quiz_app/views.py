from rest_framework import generics
from .models import Survey, Question, SurveyResponse
from .serializers import (
    SurveySerializer, QuestionSerializer, SurveyResponseSerializer, QuestionTypeSerializer
)

# Survey Views
class SurveyListView(generics.ListAPIView):
    queryset = Survey.objects.filter(is_active=True)
    serializer_class = SurveySerializer


class SurveyDetailView(generics.RetrieveAPIView):
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    lookup_field = 'slug'


# Question Views
class QuestionListView(generics.ListAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        survey_slug = self.kwargs.get('survey_slug')
        return Question.objects.filter(survey__slug=survey_slug)


# Survey Response Views
class SurveyResponseListView(generics.ListCreateAPIView):
    queryset = SurveyResponse.objects.all()
    serializer_class = SurveyResponseSerializer

    def perform_create(self, serializer):
        serializer.save(respondent=self.request.user)


class SurveyResponseDetailView(generics.RetrieveAPIView):
    queryset = SurveyResponse.objects.all()
    serializer_class = SurveyResponseSerializer


# Question Type Views
class QuestionTypeListView(generics.ListAPIView):
    queryset = QuestionType.objects.all()
    serializer_class = QuestionTypeSerializer
