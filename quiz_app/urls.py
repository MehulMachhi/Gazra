from django.urls import path
from .views import (
    SurveyListView, SurveyDetailView, QuestionListView, SurveyResponseListView, 
    SurveyResponseDetailView, QuestionTypeListView
)

urlpatterns = [
    # Survey endpoints
    path('surveys/', SurveyListView.as_view(), name='survey-list'),
    path('surveys/<slug:slug>/', SurveyDetailView.as_view(), name='survey-detail'),

    # Questions endpoints
    path('surveys/<slug:survey_slug>/questions/', QuestionListView.as_view(), name='question-list'),

    # Survey responses endpoints
    path('responses/', SurveyResponseListView.as_view(), name='survey-response-list'),
    path('responses/<int:pk>/', SurveyResponseDetailView.as_view(), name='survey-response-detail'),

    # Question types endpoint
    path('question-types/', QuestionTypeListView.as_view(), name='question-type-list'),
]
