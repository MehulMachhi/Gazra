from rest_framework.viewsets import ModelViewSet
from .models import (
    Initiative, BrainstormingSession, CommunityFeedback, NeedsAnalysis, CommunityMapping, 
    Task, Stakeholder, Event, Feedback, Risk, KPI, Milestone, Budget, ExecutionLog
)
from .serializers import (
    InitiativeSerializer, BrainstormingSessionSerializer, CommunityFeedbackSerializer, 
    NeedsAnalysisSerializer, CommunityMappingSerializer, TaskSerializer, StakeholderSerializer, 
    EventSerializer, FeedbackSerializer, RiskSerializer, KPISerializer, MilestoneSerializer, 
    BudgetSerializer, ExecutionLogSerializer
)

class InitiativeViewSet(ModelViewSet):
    queryset = Initiative.objects.all()
    serializer_class = InitiativeSerializer

class BrainstormingSessionViewSet(ModelViewSet):
    queryset = BrainstormingSession.objects.all()
    serializer_class = BrainstormingSessionSerializer

class CommunityFeedbackViewSet(ModelViewSet):
    queryset = CommunityFeedback.objects.all()
    serializer_class = CommunityFeedbackSerializer

class NeedsAnalysisViewSet(ModelViewSet):
    queryset = NeedsAnalysis.objects.all()
    serializer_class = NeedsAnalysisSerializer

class CommunityMappingViewSet(ModelViewSet):
    queryset = CommunityMapping.objects.all()
    serializer_class = CommunityMappingSerializer

class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class StakeholderViewSet(ModelViewSet):
    queryset = Stakeholder.objects.all()
    serializer_class = StakeholderSerializer

class EventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

class FeedbackViewSet(ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

class RiskViewSet(ModelViewSet):
    queryset = Risk.objects.all()
    serializer_class = RiskSerializer

class KPIViewSet(ModelViewSet):
    queryset = KPI.objects.all()
    serializer_class = KPISerializer

class MilestoneViewSet(ModelViewSet):
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer

class BudgetViewSet(ModelViewSet):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer

class ExecutionLogViewSet(ModelViewSet):
    queryset = ExecutionLog.objects.all()
    serializer_class = ExecutionLogSerializer
