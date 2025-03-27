from rest_framework import serializers
from .models import (
    Initiative, BrainstormingSession, CommunityFeedback, NeedsAnalysis, CommunityMapping, 
    Task, Stakeholder, Event, Feedback, Risk, KPI, Milestone, Budget, ExecutionLog
)

class InitiativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Initiative
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'last_updated']

class BrainstormingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrainstormingSession
        fields = '__all__'

class CommunityFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityFeedback
        fields = '__all__'

class NeedsAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = NeedsAnalysis
        fields = '__all__'

class CommunityMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityMapping
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class StakeholderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stakeholder
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'

class RiskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Risk
        fields = '__all__'

class KPISerializer(serializers.ModelSerializer):
    class Meta:
        model = KPI
        fields = '__all__'

class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = '__all__'

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = '__all__'

class ExecutionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExecutionLog
        fields = '__all__'
