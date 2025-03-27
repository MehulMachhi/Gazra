from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum, Avg
from django.contrib.admin import SimpleListFilter
from django.utils import timezone
import datetime
from .models import (
    Initiative, BrainstormingSession, CommunityFeedback, NeedsAnalysis,
    CommunityMapping, Task, Stakeholder, Event, Feedback, Risk, KPI,
    Milestone, Budget, ExecutionLog
)
import initiatives.models as models
from django.db import models



class TaskInline(admin.TabularInline):
    model = Task
    extra = 1
    fields = (
        'title',
        'assigned_to',
        'priority',
        'status',
        'start_date',
        'due_date',
        'progress',
    )
    readonly_fields = ('progress_display',)
    autocomplete_fields = ['assigned_to']
    
    def progress_display(self, obj):
        try:
            if not hasattr(obj, 'progress'):
                return mark_safe('<span style="color: gray;">N/A</span>')
            
            percentage = min(100, max(0, obj.progress))
            color = 'green' if percentage >= 75 else 'orange' if percentage >= 50 else 'red'
            width = int(percentage)
            
            return mark_safe(
                f'<div style="width:100px; background-color: #f8f9fa;">'
                f'<div style="width: {width}px; background-color: {color}; height: 20px;"></div>'
                f'<span style="color: black;">{percentage}%</span></div>'
            )
        except Exception:
            return mark_safe('<span style="color: gray;">N/A</span>')
    
    progress_display.short_description = 'Progress'

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "assigned_to":
    #         kwargs["queryset"] = Member.objects.select_related('user').all()
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)

class BudgetInline(admin.TabularInline):
    model = Budget
    extra = 1
    fields = ('item_name','quantity', 'budget_type', 'estimated_amount', 'actual_amount', 'date_required', 'approved_by')
    readonly_fields = ('approved_by',)

class KPIInline(admin.TabularInline):
    model = KPI
    extra = 1
    
    fields = (
        'name', 
        'description',
        'target_value', 
        'current_value',
        'unit_of_measure',
        'measurement_frequency',
        'data_source',
        'responsible_person',
        'baseline_value',
        'target_date',
        'achieved',
        'notes'
    )
    
    readonly_fields = ('achieved', 'achievement_percentage')
    
    autocomplete_fields = ['responsible_person']
    
    
    
    def achievement_percentage(self, obj):
        return f"{obj.achievement_percentage():.2f}%"
    achievement_percentage.short_description = "Progress"

    

class RiskInline(admin.TabularInline):
    model = Risk
    extra = 1
    fields = ('risk_type', 'description', 'risk_level', 'status', 'owner')

class MilestoneInline(admin.TabularInline):
    model = Milestone
    extra = 1
    
    fields = (
        'title',
        'description',
        'target_date',
        'actual_completion_date',
        'status',
        'progress',
        'responsible_person',
        'deliverables',
        'dependencies',
        'notes'
    )
    
    readonly_fields = ('is_delayed', 'created_at', 'updated_at')
    
    autocomplete_fields = ['responsible_person', 'dependencies']
    
    def is_delayed(self, obj):
        return "Yes" if obj.is_delayed() else "No"
    is_delayed.boolean = True
    is_delayed.short_description = "Delayed?"


class BudgetUtilizationFilter(SimpleListFilter):
    title = 'budget utilization'
    parameter_name = 'budget_utilization'

    def lookups(self, request, model_admin):
        return (
            ('under_50', 'Under 50%'),
            ('50_75', '50% - 75%'),
            ('75_90', '75% - 90%'),
            ('over_90', 'Over 90%'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'under_50':
            return queryset.filter(actual_spend__lte=0.5 * models.F('budget'))
        if self.value() == '50_75':
            return queryset.filter(
                actual_spend__gt=0.5 * models.F('budget'),
                actual_spend__lte=0.75 * models.F('budget')
            )
        if self.value() == '75_90':
            return queryset.filter(
                actual_spend__gt=0.75 * models.F('budget'),
                actual_spend__lte=0.9 * models.F('budget')
            )
        if self.value() == 'over_90':
            return queryset.filter(actual_spend__gt=0.9 * models.F('budget'))

from django.contrib import admin
from django.db.models import Count, Q, Prefetch
from django.utils import timezone
from django.urls import reverse
from django.utils.html import format_html, mark_safe
from django.db.models.functions import Coalesce
from django.contrib import messages
from django.http import HttpResponse
import csv
from datetime import datetime

@admin.register(Initiative)
class InitiativeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'status', 'department', 'sdg_alignment',
        'progress_display', 'budget_display', 'timeline_display',
        'milestones_display', 'stakeholders_display', 'kpis_display',
        'risk_count', 'budget_display', 'next_milestone', 'health_status'
    )
    list_filter = (
        'status', 'department', 'sdg_alignment',
        BudgetUtilizationFilter,
        ('start_date', admin.DateFieldListFilter),
    )
    search_fields = ('name', 'description', 'created_by__user__username')
    readonly_fields = ('created_at', 'last_updated', 'health_status')
    inlines = [KPIInline, MilestoneInline, RiskInline, BudgetInline]
    list_per_page = 20

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'department', 'status', 'sdg_alignment')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date')
        }),
        ('Financial', {
            'fields': ('budget', 'actual_spend')
        }),
        ('Target & Impact', {
            'fields': ('target_beneficiaries', 'success_metrics'),
            'classes': ('collapse',)
        }),
        ('Learning & Documentation', {
            'fields': ('challenges_faced', 'lessons_learned', 'attachments'),
            'classes': ('collapse',)
        }),
        ('Stakeholders', {
            'fields': ('stakeholders',)
        }),
        
        ('System Information', {
            'fields': ('created_by', 'created_at', 'last_updated', 'health_status'),
            'classes': ('collapse',)
        }),
        ('Student Volunteers', {
            'fields': ('volunteer',),
            # 'classes': ('collapse',)
        }),
    )
    filter_horizontal = ('stakeholders','volunteer')
    actions = ['export_as_csv', 'generate_progress_report', 'bulk_status_update']

    def get_queryset(self, request):
        """Optimize queryset with select_related and prefetch_related"""
        return super().get_queryset(request).select_related(
            'department', 'created_by'
        ).prefetch_related(
            Prefetch('kpis', queryset=KPI.objects.select_related()),
            Prefetch('milestones', queryset=Milestone.objects.select_related()),
            Prefetch('risks', queryset=Risk.objects.select_related()),
            'stakeholders'
        )

    def progress_display(self, obj):
        try:
            completed_kpis = obj.kpis.filter(achieved=True).count()
            total_kpis = obj.kpis.count()
            percentage = (completed_kpis / total_kpis * 100) if total_kpis > 0 else 0
            percentage = min(100, max(0, percentage))
            
            color = 'green' if percentage >= 75 else 'orange' if percentage >= 50 else 'red'
            width = int(percentage)
            
            return mark_safe(
                f'<div style="width:100px; background-color: #f8f9fa;">'
                f'<div style="width: {width}px; background-color: {color}; height: 20px;"></div>'
                f'<span style="color: black;">{percentage:.1f}%</span></div>'
            )
        except Exception:
            return mark_safe('<div style="color: gray;">N/A</div>')
    
    progress_display.short_description = 'Progress'

    def budget_display(self, obj):
        try:
            if not obj.budget or obj.budget == 0:
                return mark_safe('<span style="color: gray;">N/A</span>')
            
            percentage = min(100, max(0, (obj.actual_spend / obj.budget * 100)))
            color = 'red' if percentage > 90 else 'orange' if percentage > 75 else 'green'
            
            return mark_safe(
                f'<div style="width:100px;">'
                f'<span style="color: {color};">'
                f'${obj.actual_spend:,.2f} ({percentage:.1f}%)</span>'
                f'<br><small>of ${obj.budget:,.2f}</small></div>'
            )
        except Exception:
            return mark_safe('<span style="color: gray;">N/A</span>')
    
    budget_display.short_description = 'Budget Utilization'

    def timeline_display(self, obj):
        try:
            if not obj.start_date or not obj.end_date:
                return mark_safe('<span style="color: gray;">N/A</span>')
            
            total_days = (obj.end_date - obj.start_date).days
            days_passed = (timezone.now().date() - obj.start_date).days
            percentage = min(100, max(0, (days_passed / total_days * 100) if total_days > 0 else 0))
            width = int(percentage)
            
            color = 'blue'
            if percentage > 100:
                color = 'red'  # Overdue
            elif percentage > 90:
                color = 'orange'  # Near deadline
            
            return mark_safe(
                f'<div style="width:100px; background-color: #f8f9fa;">'
                f'<div style="width: {width}px; background-color: {color}; height: 20px;"></div>'
                f'<span style="color: black;">{percentage:.1f}%</span>'
                f'<br><small>{obj.end_date.strftime("%Y-%m-%d")}</small></div>'
            )
        except Exception:
            return mark_safe('<span style="color: gray;">N/A</span>')
    
    timeline_display.short_description = 'Timeline Progress'

    def milestones_display(self, obj):
        try:
            total_milestones = obj.milestones.count()
            completed_milestones = obj.milestones.filter(status='COMPLETED').count()
            percentage = (completed_milestones / total_milestones * 100) if total_milestones > 0 else 0
            
            color = 'green' if percentage == 100 else 'orange' if percentage >= 50 else 'red'
            
            return mark_safe(
                f'<div style="text-align: center;">'
                f'<span style="color: {color};">'
                f'{completed_milestones}/{total_milestones}</span>'
                f'<br><small>({percentage:.1f}%)</small></div>'
            )
        except Exception:
            return mark_safe('<span style="color: gray;">N/A</span>')
    
    milestones_display.short_description = 'Milestones'

    def stakeholders_display(self, obj):
        try:
            count = obj.stakeholders.count()
            return format_html(
                '<div style="text-align: center;">'
                '<a href="{}?id__in={}">{}</a>'
                '<br><small>stakeholders</small></div>',
                reverse('admin:initiatives_stakeholder_changelist'),
                ','.join(str(x) for x in obj.stakeholders.values_list('id', flat=True)),
                count
            )
        except Exception:
            return mark_safe('<span style="color: gray;">N/A</span>')
    
    stakeholders_display.short_description = 'Stakeholders'

    def kpis_display(self, obj):
        try:
            total_kpis = obj.kpis.count()
            achieved_kpis = obj.kpis.filter(achieved=True).count()
            percentage = (achieved_kpis / total_kpis * 100) if total_kpis > 0 else 0
            
            color = 'green' if percentage == 100 else 'orange' if percentage >= 50 else 'red'
            
            return mark_safe(
                f'<div style="text-align: center;">'
                f'<span style="color: {color};">'
                f'{achieved_kpis}/{total_kpis}</span>'
                f'<br><small>({percentage:.1f}%)</small></div>'
            )
        except Exception:
            return mark_safe('<span style="color: gray;">N/A</span>')
    
    kpis_display.short_description = 'KPIs'

    def risk_count(self, obj):
        try:
            high_risks = obj.risks.filter(risk_level__in=['HIGH', 'CRITICAL']).count()
            total_risks = obj.risks.count()
            
            color = 'red' if high_risks > 0 else 'green'
            
            return mark_safe(
                f'<div style="text-align: center;">'
                f'<span style="color: {color};">'
                f'{total_risks} total</span>'
                f'<br><small>{high_risks} critical ⚠️</small></div>'
            )
        except Exception:
            return mark_safe('<span style="color: gray;">N/A</span>')
    
    risk_count.short_description = 'Risks'

    def next_milestone(self, obj):
        """Display the next upcoming milestone"""
        try:
            next_milestone = obj.milestones.filter(
                status='PENDING',
                due_date__gte=timezone.now().date()
            ).order_by('due_date').first()
            
            if not next_milestone:
                return mark_safe('<span style="color: gray;">No upcoming</span>')
            
            days_until = (next_milestone.due_date - timezone.now().date()).days
            color = 'red' if days_until <= 7 else 'orange' if days_until <= 14 else 'green'
            
            return mark_safe(
                f'<div style="text-align: center;">'
                f'<span style="color: {color};">'
                f'{next_milestone.title[:20]}...</span>'
                f'<br><small>in {days_until} days</small></div>'
            )
        except Exception:
            return mark_safe('<span style="color: gray;">N/A</span>')
    
    next_milestone.short_description = 'Next Milestone'

    def health_status(self, obj):
        """Calculate overall initiative health based on multiple factors"""
        try:
            # Calculate various health indicators
            timeline_health = self._calculate_timeline_health(obj)
            budget_health = self._calculate_budget_health(obj)
            risk_health = self._calculate_risk_health(obj)
            progress_health = self._calculate_progress_health(obj)
            
            # Weight and combine health indicators
            overall_health = (
                timeline_health * 0.3 +
                budget_health * 0.3 +
                risk_health * 0.2 +
                progress_health * 0.2
            )
            
            # Determine status and color
            if overall_health >= 80:
                status, color = 'Healthy', 'green'
            elif overall_health >= 60:
                status, color = 'At Risk', 'orange'
            else:
                status, color = 'Critical', 'red'
            
            return mark_safe(
                f'<div style="text-align: center;">'
                f'<span style="color: {color};">{status}</span>'
                f'<br><small>{overall_health:.1f}%</small></div>'
            )
        except Exception:
            return mark_safe('<span style="color: gray;">N/A</span>')
    
    health_status.short_description = 'Health Status'

    def _calculate_timeline_health(self, obj):
        """Helper method to calculate timeline health percentage"""
        try:
            if not obj.start_date or not obj.end_date:
                return 100
            
            total_days = (obj.end_date - obj.start_date).days
            days_passed = (timezone.now().date() - obj.start_date).days
            if total_days <= 0:
                return 0
            
            percentage = (days_passed / total_days * 100)
            return max(0, 100 - max(0, percentage - 100))
        except Exception:
            return 0

    def _calculate_budget_health(self, obj):
        """Helper method to calculate budget health percentage"""
        try:
            if not obj.budget or obj.budget == 0:
                return 100
            
            percentage = (obj.actual_spend / obj.budget * 100)
            return max(0, 100 - max(0, percentage - 100))
        except Exception:
            return 0

    def _calculate_risk_health(self, obj):
        """Helper method to calculate risk health percentage"""
        try:
            high_risks = obj.risks.filter(risk_level__in=['HIGH', 'CRITICAL']).count()
            total_risks = obj.risks.count()
            if total_risks == 0:
                return 100
            
            return max(0, 100 - (high_risks / total_risks * 100))
        except Exception:
            return 0

    def _calculate_progress_health(self, obj):
        """Helper method to calculate progress health percentage"""
        try:
            completed_kpis = obj.kpis.filter(achieved=True).count()
            total_kpis = obj.kpis.count()
            if total_kpis == 0:
                return 100
            
            return (completed_kpis / total_kpis * 100)
        except Exception:
            return 0

    def export_as_csv(self, request, queryset):
        """Export selected initiatives as CSV"""
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta.verbose_name_plural}.csv'
        
        writer = csv.writer(response)
        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        
        return response
    
    export_as_csv.short_description = "Export selected initiatives as CSV"

@admin.register(BrainstormingSession)
class BrainstormingSessionAdmin(admin.ModelAdmin):
    list_display = (
        'initiative', 'session_type', 'date',
        'facilitator', 'participants_count', 'location'
    )
    list_filter = ('session_type', 'date', 'initiative')
    search_fields = ('initiative__name', 'agenda', 'summary')
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Session Information', {
            'fields': ('initiative', 'session_type', 'date', 'location', 'facilitator')
        }),
        ('Participation', {
            'fields': ('participants_count', 'materials_used')
        }),
        ('Content', {
            'fields': ('agenda', 'summary', 'key_outcomes', 'next_steps')
        }),
        ('Additional Information', {
            'fields': ('notes', 'attachments', 'feedback_summary'),
            'classes': ('collapse',)
        }),
    )

@admin.register(CommunityFeedback)
class CommunityFeedbackAdmin(admin.ModelAdmin):
    list_display = (
        'initiative', 'feedback_type', 'priority',
        'status', 'feedback_date', 'assigned_to'
    )
    list_filter = ('feedback_type', 'priority', 'status', 'feedback_date')
    search_fields = ('feedback_text', 'initiative__name', 'submitted_by')
    readonly_fields = ('feedback_date',)

    fieldsets = (
        ('Feedback Information', {
            'fields': (
                'initiative', 'feedback_type', 'feedback_text',
                'category', 'priority'
            )
        }),
        ('Submission Details', {
            'fields': (
                'submitted_by', 'contact_info', 'is_anonymous'
            )
        }),
        ('Response', {
            'fields': (
                'status', 'assigned_to', 'response_text',
                'response_date'
            )
        }),
    )

@admin.register(NeedsAnalysis)
class NeedsAnalysisAdmin(admin.ModelAdmin):
    list_display = (
        'initiative', 'target_group', 'priority_level',
        'estimated_budget', 'created_by'
    )
    list_filter = ('priority_level', 'created_at')
    search_fields = (
        'initiative__name', 'target_group',
        'identified_need', 'proposed_solution'
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(CommunityMapping)
class CommunityMappingAdmin(admin.ModelAdmin):
    list_display = (
        'initiative', 'area_name', 'population_size',
        'mapped_by', 'mapping_date'
    )
    list_filter = ('mapping_date', 'initiative')
    search_fields = ('area_name', 'demographic_data', 'key_stakeholders')
    readonly_fields = ('last_updated',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'initiative', 
        'milestone',
        'assigned_to',
        'priority', 
        'status', 
        'progress_bar',  # Changed from progress_display
        'due_date'
    )
    
    list_filter = (
        'priority', 
        'status', 
        'due_date',
        'milestone'
    )
    
    search_fields = (
        'title', 
        'description', 
        'initiative__name',
        'milestone__title'
    )
    
    readonly_fields = (
        'created_at', 
        'updated_at',
        'progress_bar'
    )
    
    autocomplete_fields = ['milestone', 'assigned_to', 'dependencies']

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'initiative',
                'milestone',
                'title',
                'description'
            )
        }),
        ('Assignment', {
            'fields': (
                'assigned_to',
                'priority',
                'status'
            )
        }),
        ('Timeline', {
            'fields': (
                'start_date',
                'due_date',
                'completion_date'
            )
        }),
        ('Progress', {
            'fields': (
                'progress',
                'progress_bar',  # Added progress bar to fields
                'dependencies'
            )
        }),
        ('Additional Information', {
            'fields': (
                'comments',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )

    def progress_bar(self, obj):
        """Display progress as a colored bar"""
        try:
            if not hasattr(obj, 'progress'):
                return mark_safe('<span style="color: gray;">N/A</span>')
            
            percentage = min(100, max(0, obj.progress))
            color = 'green' if percentage >= 75 else 'orange' if percentage >= 50 else 'red'
            width = int(percentage)
            
            return mark_safe(
                f'<div style="width:100px; background-color: #f8f9fa;">'
                f'<div style="width: {width}px; background-color: {color}; '
                f'height: 20px; display: inline-block;"></div>'
                f'<span style="color: black; margin-left: 4px;">{percentage}%</span></div>'
            )
        except Exception:
            return mark_safe('<span style="color: gray;">N/A</span>')
    
    progress_bar.short_description = 'Progress'
    progress_bar.allow_tags = True

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     """Customize foreign key querysets"""
    #     if db_field.name == "assigned_to":
    #         kwargs["queryset"] = Member.objects.select_related('user').all()
    #     elif db_field.name == "initiative":
    #         kwargs["queryset"] = Initiative.objects.all().order_by('name')
    #     elif db_field.name == "milestone":
    #         if 'initiative' in request.GET:
    #             kwargs["queryset"] = Milestone.objects.filter(
    #                 initiative_id=request.GET['initiative']
    #             )
    #         else:
    #             kwargs["queryset"] = Milestone.objects.all()
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        """Optimize queryset for admin list view"""
        return super().get_queryset(request).select_related(
            'initiative',
            'milestone',
            'assigned_to',
            'assigned_to__user'
        )

    def save_model(self, request, obj, form, change):
        """Custom save logic"""
        if obj.progress == 100 and not obj.completion_date:
            obj.completion_date = timezone.now().date()
            obj.status = 'COMPLETED'
        elif obj.progress == 0:
            obj.status = 'TODO'
        elif obj.progress > 0 and obj.progress < 100:
            obj.status = 'IN_PROGRESS'
        super().save_model(request, obj, form, change)

    class Media:
        css = {
            'all': ('admin/css/forms.css',)
        }

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'initiative', 'event_type', 'start_date',
        'status', 'participant_count', 'budget_status'
    )
    list_filter = ('event_type', 'status', 'start_date')
    search_fields = ('name', 'description', 'initiative__name')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('speakers', 'volunteers')

    def participant_count(self, obj):
        try:
            return mark_safe(
                f'{obj.current_participants} / {obj.max_participants} '
                f'{"(FULL)" if obj.is_full() else ""}'
            )
        except Exception:
            return mark_safe('<span style="color: gray;">N/A</span>')
    
    participant_count.short_description = 'Participants'

    def budget_status(self, obj):
        try:
            if not obj.budget or obj.budget == 0:
                return mark_safe('<span style="color: gray;">N/A</span>')
            
            percentage = min(100, max(0, (obj.actual_spend / obj.budget * 100)))
            color = 'red' if percentage > 100 else 'green'
            
            return mark_safe(
                f'<span style="color: {color};">'
                f'${obj.actual_spend:,.2f} ({percentage:.1f}%)</span>'
            )
        except Exception:
            return mark_safe('<span style="color: gray;">N/A</span>')
    
    budget_status.short_description = 'Budget Status'

@admin.register(Risk)
class RiskAdmin(admin.ModelAdmin):
    list_display = (
        'initiative', 'risk_type', 'risk_level_display',
        'probability', 'impact', 'risk_score_display',
        'status', 'owner'
    )
    list_filter = ('risk_type', 'risk_level', 'status')
    search_fields = ('description', 'initiative__name', 'mitigation_plan')
    readonly_fields = ('created_at', 'updated_at')

    def risk_level_display(self, obj):
        try:
            colors = {
                'LOW': 'green',
                'MEDIUM': 'orange',
                'HIGH': 'red',
                'CRITICAL': 'darkred'
            }
            return mark_safe(
                f'<span style="color: {colors.get(obj.risk_level, "black")};">'
                f'{obj.get_risk_level_display()}</span>'
            )
        except Exception:
            return mark_safe('<span style="color: gray;">N/A</span>')
    
    risk_level_display.short_description = 'Risk Level'

    def risk_score_display(self, obj):
        try:
            if not hasattr(obj, 'risk_score'):
                return mark_safe('<span style="color: gray;">N/A</span>')
            
            score = obj.risk_score()
            color = 'red' if score > 15 else 'orange' if score > 10 else 'green'
            
            return mark_safe(
                f'<span style="color: {color};">{score}</span>'
            )
        except Exception:
            return mark_safe('<span style="color: gray;">N/A</span>')
    
    risk_score_display.short_description = 'Risk Score'

@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'initiative', 'target_value',
        'current_value', 'progress_display',
        'achieved', 'target_date'
    )
    list_filter = ('achieved', 'measurement_frequency', 'target_date')
    search_fields = ('name', 'description', 'initiative__name')
    readonly_fields = ('created_at', 'updated_at')

    def progress_display(self, obj):
        try:
            if not hasattr(obj, 'achievement_percentage'):
                return mark_safe('<span style="color: gray;">N/A</span>')
            
            percentage = min(100, max(0, obj.achievement_percentage()))
            color = 'green' if percentage >= 100 else 'orange' if percentage >= 75 else 'red'
            
            return mark_safe(
                f'<span style="color: {color};">{percentage:.1f}%</span>'
            )
        except Exception:
            return mark_safe('<span style="color: gray;">N/A</span>')
    
    progress_display.short_description = 'Progress'

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'initiative',
        'responsible_person', 
        'target_date',
        'status', 
        'progress_display',
        'delay_status',
        'get_tasks_count'  # Changed from tasks_count to get_tasks_count
    )
    list_filter = (
        'status', 
        'target_date',
        'initiative'
    )
    search_fields = (
        'title', 
        'description', 
        'initiative__name'
    )
    readonly_fields = (
        'created_at', 
        'updated_at', 
        'tasks_summary',
        'get_tasks_count'  # Added to readonly_fields
    )
    inlines = [TaskInline]

    def get_tasks_count(self, obj):
        """Display count of total and completed tasks"""
        if not obj.pk:
            return "0/0"
        total_tasks = obj.milestone_tasks.count()  # Using related_name from Task model
        completed_tasks = obj.milestone_tasks.filter(status='COMPLETED').count()
        return format_html(
            '<span title="Completed/Total Tasks" style="white-space: nowrap;">'
            '<strong style="color: green;">{}</strong>/{}</span>',
            completed_tasks,
            total_tasks
        )
    get_tasks_count.short_description = 'Tasks (Done/Total)'
    get_tasks_count.admin_order_field = 'milestone_tasks__count'

    def get_queryset(self, request):
        """Optimize queryset with annotations"""
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            tasks_count=Count('milestone_tasks'),
            completed_tasks_count=Count(
                'milestone_tasks',
                filter=models.Q(milestone_tasks__status='COMPLETED')
            )
        )
        return queryset

    def tasks_summary(self, obj):
        """Detailed summary of tasks"""
        if not obj.pk:
            return "-"
        
        tasks = obj.milestone_tasks.all()
        total = tasks.count()
        if not total:
            return "No tasks created yet"
        
        # Get task statistics
        completed = tasks.filter(status='COMPLETED').count()
        in_progress = tasks.filter(status='IN_PROGRESS').count()
        pending = tasks.filter(status='TODO').count()
        delayed = tasks.filter(
            due_date__lt=timezone.now().date()
        ).exclude(status='COMPLETED').count()
        
        # Calculate average progress
        avg_progress = tasks.aggregate(
            avg_progress=Avg('progress')
        )['avg_progress'] or 0
        
        summary = f"""
        <div style="margin-bottom: 10px;">
            <strong>Tasks Overview:</strong><br>
            Total Tasks: {total}<br>
            Completed: <span style="color: green;">{completed}</span><br>
            In Progress: <span style="color: blue;">{in_progress}</span><br>
            Pending: <span style="color: orange;">{pending}</span><br>
            Delayed: <span style="color: red;">{delayed}</span><br>
            Average Progress: {avg_progress:.1f}%
        </div>
        """
        return mark_safe(summary)
    tasks_summary.short_description = 'Tasks Summary'

    def progress_display(self, obj):
        """Display progress bar"""
        try:
            if not hasattr(obj, 'progress'):
                return mark_safe('<span style="color: gray;">N/A</span>')
            
            percentage = min(100, max(0, obj.progress))
            color = 'green' if percentage >= 75 else 'orange' if percentage >= 50 else 'red'
            width = int(percentage)
            
            return mark_safe(
                f'<div style="width:100px; background-color: #f8f9fa;">'
                f'<div style="width: {width}px; background-color: {color}; height: 20px;"></div>'
                f'<span style="color: black;">{percentage}%</span></div>'
            )
        except Exception:
            return mark_safe('<span style="color: gray;">N/A</span>')
    progress_display.short_description = 'Progress'

    def delay_status(self, obj):
        """Display delay status"""
        try:
            if obj.status == 'COMPLETED':
                return mark_safe('<span style="color: green;">Completed</span>')

            if not obj.target_date:
                return mark_safe('<span style="color: gray;">N/A</span>')

            today = timezone.now().date()
            if obj.target_date < today:
                days_delayed = (today - obj.target_date).days
                return mark_safe(
                    f'<span style="color: red;">Delayed by {days_delayed} days</span>'
                )

            days_remaining = (obj.target_date - today).days
            return mark_safe(
                f'<span style="color: green;">{days_remaining} days remaining</span>'
            )
        except Exception:
            return mark_safe('<span style="color: gray;">N/A</span>')
    delay_status.short_description = 'Timeline Status'

    class Media:
        css = {
            'all': ('admin/css/forms.css',)
        }
    
@admin.register(Stakeholder)
class StakeholderAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'organization_type', 
        'contact_person',
        'involvement_level',
        'initiatives_count',
        'last_contact_status'
    )
    list_filter = (
        'organization_type', 
        'involvement_level',
        'last_contact'
    )
    search_fields = (
        'name', 
        'contact_person', 
        'email', 
        'contribution_type'
    )
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name', 
                'organization_type', 
                'involvement_level'
            )
        }),
        ('Contact Details', {
            'fields': (
                'contact_person',
                'email',
                'phone',
                'address'
            )
        }),
        ('Engagement Details', {
            'fields': (
                'resources_provided',
                'expectations',
                'contribution_type',
                'last_contact'
            )
        }),
        ('Additional Information', {
            'fields': (
                'notes',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )

    def initiatives_count(self, obj):
        count = obj.initiatives.count()
        return format_html(
            '<a href="{}?stakeholders__id={}">{} initiatives</a>',
            reverse('admin:initiatives_initiative_changelist'),
            obj.id,
            count
        )
    initiatives_count.short_description = 'Initiatives'

    def last_contact_status(self, obj):
        if not obj.last_contact:
            return mark_safe('<span style="color: gray;">No contact recorded</span>')
        
        days_since = (timezone.now().date() - obj.last_contact).days
        if days_since > 90:
            color = 'red'
        elif days_since > 30:
            color = 'orange'
        else:
            color = 'green'
        
        return mark_safe(
            f'<span style="color: {color};">{days_since} days ago</span>'
        )
    last_contact_status.short_description = 'Last Contact'

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = (
        'item_name',
        'initiative',
        'budget_type',
        'estimated_amount',
        'actual_amount',
        'variance_display',
        'approval_status',
        'date_required'
    )
    list_filter = (
        'budget_type',
        'approval_date',
        'date_required',
        'initiative'
    )
    search_fields = (
        'item_name',
        'description',
        'initiative__name'
    )
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'initiative',
                'item_name',
                'description',
                'budget_type'
            )
        }),
        ('Financial Details', {
            'fields': (
                'estimated_amount',
                'actual_amount',
                'quantity',
                'unit_cost'
            )
        }),
        ('Approval Information', {
            'fields': (
                'approved_by',
                'approval_date',
                'date_required',
                'variance_explanation'
            )
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def variance_display(self, obj):
        try:
            variance = obj.variance_amount()
            percentage = obj.variance_percentage()
            color = 'red' if variance > 0 else 'green'
            
            return mark_safe(
                f'<span style="color: {color};">'
                f'₹{variance:,.2f} ({percentage:.1f}%)</span>'
            )
        except Exception:
            return mark_safe('<span style="color: gray;">N/A</span>')
    variance_display.short_description = 'Variance'

    def approval_status(self, obj):
        if obj.approval_date and obj.approved_by:
            return mark_safe(
                f'<span style="color: green;">Approved by {obj.approved_by}</span>'
            )
        return mark_safe('<span style="color: orange;">Pending</span>')
    approval_status.short_description = 'Approval Status'

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        'event',
        'participant_display',
        'rating_display',
        'would_recommend',
        'submitted_at'
    )
    list_filter = (
        'rating',
        'would_recommend',
        'is_anonymous',
        'submitted_at'
    )
    search_fields = (
        'event__name',
        'participant_name',
        'feedback_text',
        'suggestions'
    )
    readonly_fields = ('submitted_at',)

    fieldsets = (
        ('Event Information', {
            'fields': ('event',)
        }),
        ('Feedback Details', {
            'fields': (
                'rating',
                'feedback_text',
                'suggestions',
                'would_recommend',
                'areas_of_improvement'
            )
        }),
        ('Participant Information', {
            'fields': (
                'participant_name',
                'email',
                'is_anonymous'
            )
        }),
    )

    def participant_display(self, obj):
        if obj.is_anonymous:
            return mark_safe('<em>Anonymous</em>')
        return obj.participant_name or mark_safe('<span style="color: gray;">N/A</span>')
    participant_display.short_description = 'Participant'

    def rating_display(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        color = 'green' if obj.rating >= 4 else 'orange' if obj.rating >= 3 else 'red'
        return mark_safe(f'<span style="color: {color};">{stars}</span>')
    rating_display.short_description = 'Rating'

@admin.register(ExecutionLog)
class ExecutionLogAdmin(admin.ModelAdmin):
    list_display = (
        'initiative',
        'date',
        'participant_count',
        'has_photos',
        'created_by',
        'created_at'
    )
    list_filter = ('date', 'created_at', 'initiative')
    search_fields = (
        'activity',
        'outcomes',
        'challenges',
        'initiative__name'
    )
    readonly_fields = ('created_at',)
    filter_horizontal = ('participants',)

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'initiative',
                'date',
                'activity',
                'outcomes'
            )
        }),
        ('Execution Details', {
            'fields': (
                'challenges',
                'participants',
                'photos',
                'notes'
            )
        }),
        ('System Information', {
            'fields': (
                'created_by',
                'created_at'
            ),
            'classes': ('collapse',)
        }),
    )

    def participant_count(self, obj):
        count = obj.participants.count()
        return f"{count} participant{'s' if count != 1 else ''}"
    participant_count.short_description = 'Participants'

    def has_photos(self, obj):
        return bool(obj.photos)
    has_photos.boolean = True
    has_photos.short_description = 'Has Photos'