from rest_framework.routers import DefaultRouter
from .views import (
    InitiativeViewSet, BrainstormingSessionViewSet, CommunityFeedbackViewSet, 
    NeedsAnalysisViewSet, CommunityMappingViewSet, TaskViewSet, StakeholderViewSet, 
    EventViewSet, FeedbackViewSet, RiskViewSet, KPIViewSet, MilestoneViewSet, 
    BudgetViewSet, ExecutionLogViewSet
)

router = DefaultRouter()
router.register(r'initiatives', InitiativeViewSet)
router.register(r'brainstorming-sessions', BrainstormingSessionViewSet)
router.register(r'community-feedback', CommunityFeedbackViewSet)
router.register(r'needs-analyses', NeedsAnalysisViewSet)
router.register(r'community-mappings', CommunityMappingViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'stakeholders', StakeholderViewSet)
router.register(r'events', EventViewSet)
router.register(r'feedback', FeedbackViewSet)
router.register(r'risks', RiskViewSet)
router.register(r'kpis', KPIViewSet)
router.register(r'milestones', MilestoneViewSet)
router.register(r'budgets', BudgetViewSet)
router.register(r'execution-logs', ExecutionLogViewSet)

urlpatterns = router.urls
