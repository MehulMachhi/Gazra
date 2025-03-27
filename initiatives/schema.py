import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_jwt.decorators import login_required
from django.core.exceptions import ValidationError
from .models import (
    Initiative , Event , Stakeholder , BrainstormingSession ,
    CommunityFeedback , NeedsAnalysis , CommunityMapping ,
    Task , Risk , KPI , Milestone , Budget , ExecutionLog
)


# Types
class InitiativeType(DjangoObjectType):
    class Meta:
        model = Initiative
        filter_fields = {
            'name': ['exact' , 'icontains'] ,
            'status': ['exact'] ,
            'sdg_alignment': ['exact'] ,
            'department': ['exact'] ,
            'start_date': ['gte' , 'lte'] ,
            'end_date': ['gte' , 'lte'] ,
            'created_at': ['gte' , 'lte'] ,
        }
        interfaces = (graphene.relay.Node ,)


class EventType(DjangoObjectType):
    class Meta:
        model = Event
        filter_fields = {
            'name': ['exact' , 'icontains'] ,
            'status': ['exact'] ,
            'event_type': ['exact'] ,
            'start_date': ['gte' , 'lte'] ,
            'initiative': ['exact'] ,
        }
        interfaces = (graphene.relay.Node ,)


class StakeholderType(DjangoObjectType):
    class Meta:
        model = Stakeholder
        filter_fields = {
            'name': ['exact' , 'icontains'] ,
            'organization_type': ['exact'] ,
            'involvement_level': ['exact'] ,
        }
        interfaces = (graphene.relay.Node ,)


class BrainstormingSessionType(DjangoObjectType):
    class Meta:
        model = BrainstormingSession
        filter_fields = {
            'session_type': ['exact'] ,
            'date': ['gte' , 'lte'] ,
            'initiative': ['exact'] ,
        }
        interfaces = (graphene.relay.Node ,)


class TaskType(DjangoObjectType):
    class Meta:
        model = Task
        filter_fields = {
            'status': ['exact'] ,
            'priority': ['exact'] ,
            'initiative': ['exact'] ,
            'assigned_to': ['exact'] ,
            'due_date': ['gte' , 'lte'] ,
        }
        interfaces = (graphene.relay.Node ,)


class RiskType(DjangoObjectType):
    class Meta:
        model = Risk
        filter_fields = {
            'risk_level': ['exact'] ,
            'risk_type': ['exact'] ,
            'status': ['exact'] ,
            'initiative': ['exact'] ,
        }
        interfaces = (graphene.relay.Node ,)


class KPIType(DjangoObjectType):
    class Meta:
        model = KPI
        filter_fields = {
            'achieved': ['exact'] ,
            'measurement_frequency': ['exact'] ,
            'initiative': ['exact'] ,
        }
        interfaces = (graphene.relay.Node ,)


# Queries
class Query(graphene.ObjectType):
    # Single item queries
    initiative = graphene.relay.Node.Field(InitiativeType)
    event = graphene.relay.Node.Field(EventType)
    stakeholder = graphene.relay.Node.Field(StakeholderType)
    task = graphene.relay.Node.Field(TaskType)
    risk = graphene.relay.Node.Field(RiskType)
    kpi = graphene.relay.Node.Field(KPIType)

    # List queries
    all_initiatives = DjangoFilterConnectionField(InitiativeType)
    all_events = DjangoFilterConnectionField(EventType)
    all_stakeholders = DjangoFilterConnectionField(StakeholderType)
    all_tasks = DjangoFilterConnectionField(TaskType)
    all_risks = DjangoFilterConnectionField(RiskType)
    all_kpis = DjangoFilterConnectionField(KPIType)

    # Custom queries
    my_initiatives = DjangoFilterConnectionField(InitiativeType)
    my_tasks = DjangoFilterConnectionField(TaskType)
    upcoming_events = DjangoFilterConnectionField(EventType)
    high_priority_risks = DjangoFilterConnectionField(RiskType)

    @login_required
    def resolve_my_initiatives(self , info , **kwargs):
        return Initiative.objects.filter(created_by=info.context.user)

    @login_required
    def resolve_my_tasks(self , info , **kwargs):
        return Task.objects.filter(assigned_to=info.context.user)

    @login_required
    def resolve_upcoming_events(self , info , **kwargs):
        from django.utils import timezone
        return Event.objects.filter(start_date__gte=timezone.now())

    @login_required
    def resolve_high_priority_risks(self , info , **kwargs):
        return Risk.objects.filter(risk_level__in=['HIGH' , 'CRITICAL'])


# Input Types
class InitiativeInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    description = graphene.String(required=True)
    start_date = graphene.Date(required=True)
    end_date = graphene.Date(required=True)
    budget = graphene.Decimal(required=True)
    sdg_alignment = graphene.String(required=True)
    department_id = graphene.ID(required=True)
    target_beneficiaries = graphene.String(required=True)
    success_metrics = graphene.String(required=True)
    stakeholder_ids = graphene.List(graphene.ID)


# Mutations
class CreateInitiativeMutation(graphene.Mutation):
    class Arguments:
        input = InitiativeInput(required=True)

    initiative = graphene.Field(InitiativeType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @login_required
    def mutate(self , info , input):
        try:
            stakeholders = []
            if input.get('stakeholder_ids'):
                stakeholders = Stakeholder.objects.filter(
                    id__in=input.pop('stakeholder_ids')
                )

            initiative = Initiative.objects.create(
                created_by=info.context.user ,
                **input
            )

            if stakeholders:
                initiative.stakeholders.set(stakeholders)

            return CreateInitiativeMutation(
                initiative=initiative ,
                success=True ,
                errors=None
            )
        except ValidationError as e:
            return CreateInitiativeMutation(
                initiative=None ,
                success=False ,
                errors=[str(e)]
            )


class UpdateInitiativeMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        input = InitiativeInput(required=True)

    initiative = graphene.Field(InitiativeType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @login_required
    def mutate(self , info , id , input):
        try:
            initiative = Initiative.objects.get(pk=id)

            # Update fields
            for key , value in input.items():
                setattr(initiative , key , value)

            initiative.save()

            return UpdateInitiativeMutation(
                initiative=initiative ,
                success=True ,
                errors=None
            )
        except Initiative.DoesNotExist:
            return UpdateInitiativeMutation(
                initiative=None ,
                success=False ,
                errors=["Initiative not found"]
            )
        except ValidationError as e:
            return UpdateInitiativeMutation(
                initiative=None ,
                success=False ,
                errors=[str(e)]
            )


class DeleteInitiativeMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @login_required
    def mutate(self , info , id):
        try:
            initiative = Initiative.objects.get(pk=id)
            initiative.delete()
            return DeleteInitiativeMutation(success=True , errors=None)
        except Initiative.DoesNotExist:
            return DeleteInitiativeMutation(
                success=False ,
                errors=["Initiative not found"]
            )


class Mutation(graphene.ObjectType):
    create_initiative = CreateInitiativeMutation.Field()
    update_initiative = UpdateInitiativeMutation.Field()
    delete_initiative = DeleteInitiativeMutation.Field()


schema = graphene.Schema(query=Query , mutation=Mutation)