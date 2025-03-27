# monitoring/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Avg
from .models import (
    KPIMetric , MetricProgress , ParticipantFeedback ,
    MonitoringCheckIn , DataCollectionTemplate , MonitoringReport
)

from .models import (
    EmploymentTracking, SkillAssessment, WeeklyProgress,
    QuarterlyImpactReview, FinancialTracking
)
class MetricProgressInline(admin.TabularInline):
    model = MetricProgress
    extra = 1
    fields = ('value' , 'date_recorded' , 'recorded_by' , 'notes')





@admin.register(KPIMetric)
class KPIMetricAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'name' , 'initiative' , 'metric_type' ,
        'progress_display' , 'monitoring_frequency' ,
        'responsible_person' , 'status_display'
    )
    list_filter = (
        'metric_type' , 'monitoring_frequency' ,
        'start_date' , 'initiative'
    )
    search_fields = ('name' , 'description' , 'initiative__name')
    inlines = [MetricProgressInline]

    fieldsets = (
        ('Basic Information' , {
            'fields': (
                'initiative' , 'name' , 'metric_type' ,
                'description'
            )
        }) ,
        ('Targets & Measurement' , {
            'fields': (
                'target_value' , 'current_value' ,
                'unit_of_measure' , 'monitoring_frequency'
            )
        }) ,
        ('Timeline' , {
            'fields': ('start_date' , 'end_date')
        }) ,
        ('Responsibility' , {
            'fields': (
                'responsible_person' ,
                'data_collection_method'
            )
        }) ,
        ('Additional Information' , {
            'fields': ('notes' ,) ,
            'classes': ('collapse' ,)
        })
    )

    def progress_display(self , obj):
        percentage = obj.completion_percentage()
        color = 'green' if percentage >= 75 else 'orange' if percentage >= 50 else 'red'
        return format_html(
            '<div style="width:100px; background-color: #f8f9fa;">'
            '<div style="width: {}px; background-color: {}; height: 20px;"></div>'
            '<span style="color: black;">{:.1f}%</span></div>' ,
            percentage ,
            color ,
            percentage
        )

    progress_display.short_description = 'Progress'

    def status_display(self , obj):
        if obj.current_value >= obj.target_value:
            return format_html('<span style="color: green;">Target Achieved</span>')
        if obj.end_date < timezone.now().date():
            return format_html('<span style="color: red;">Overdue</span>')
        return format_html('<span style="color: blue;">In Progress</span>')

    status_display.short_description = 'Status'


@admin.register(ParticipantFeedback)
class ParticipantFeedbackAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'event' , 'participant_display' , 'satisfaction_display' ,
        'confidence_improvement' , 'would_recommend' ,
        'submission_date'
    )
    list_filter = (
        'satisfaction_rating' , 'would_recommend' ,
        'employment_status' , 'event'
    )
    search_fields = (
        'participant_name' , 'most_valuable_aspect' ,
        'improvement_suggestions'
    )

    fieldsets = (
        ('Basic Information' , {
            'fields': (
                'event' , 'participant_name' , 'email' ,
                'is_anonymous'
            )
        }) ,
        ('Feedback' , {
            'fields': (
                'satisfaction_rating' , 'most_valuable_aspect' ,
                'improvement_suggestions' , 'would_recommend'
            )
        }) ,
        ('Impact Assessment' , {
            'fields': (
                'skills_gained' , 'confidence_improvement' ,
                'employment_status'
            )
        })
    )

    def participant_display(self , obj):
        return 'Anonymous' if obj.is_anonymous else obj.participant_name

    participant_display.short_description = 'Participant'

    def satisfaction_display(self , obj):
        stars = '★' * obj.satisfaction_rating + '☆' * (5 - obj.satisfaction_rating)
        color = 'green' if obj.satisfaction_rating >= 4 else 'orange' if obj.satisfaction_rating >= 3 else 'red'
        return format_html(
            '<span style="color: {};">{}</span>' ,
            color ,
            stars
        )

    satisfaction_display.short_description = 'Satisfaction'


@admin.register(MonitoringCheckIn)
class MonitoringCheckInAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'initiative' , 'check_in_type' , 'date' ,
        'conducted_by' , 'attendees_count' , 'has_attachments'
    )
    list_filter = ('check_in_type' , 'date' , 'initiative')
    search_fields = (
        'progress_summary' , 'challenges_identified' ,
        'action_items'
    )
    filter_horizontal = ('attendees' ,)

    fieldsets = (
        ('Basic Information' , {
            'fields': (
                'initiative' , 'check_in_type' , 'date' ,
                'conducted_by'
            )
        }) ,
        ('Attendance' , {
            'fields': ('attendees' ,)
        }) ,
        ('Check-in Details' , {
            'fields': (
                'progress_summary' , 'challenges_identified' ,
                'action_items' , 'next_steps'
            )
        }) ,
        ('Documentation' , {
            'fields': ('attachments' ,) ,
            'classes': ('collapse' ,)
        })
    )

    def attendees_count(self , obj):
        count = obj.attendees.count()
        return f"{count} attendees"

    attendees_count.short_description = 'Attendance'

    def has_attachments(self , obj):
        return bool(obj.attachments)

    has_attachments.boolean = True
    has_attachments.short_description = 'Has Attachments'


@admin.register(DataCollectionTemplate)
class DataCollectionTemplateAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'name' , 'template_type' , 'created_by' ,
        'is_active' , 'created_at'
    )
    list_filter = ('template_type' , 'is_active' , 'created_at')
    search_fields = ('name' , 'description' , 'instructions')

    fieldsets = (
        ('Basic Information' , {
            'fields': (
                'name' , 'template_type' , 'description' ,
                'is_active'
            )
        }) ,
        ('Template Details' , {
            'fields': ('fields' , 'instructions')
        }) ,
        ('Ownership' , {
            'fields': ('created_by' ,)
        })
    )


@admin.register(MonitoringReport)
class MonitoringReportAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'initiative' , 'report_type' , 'period_display' ,
        'status' , 'prepared_by' , 'review_status'
    )
    list_filter = ('report_type' , 'status' , 'period_start')
    search_fields = (
        'executive_summary' , 'program_highlights' ,
        'initiative__name'
    )

    fieldsets = (
        ('Report Information' , {
            'fields': (
                'initiative' , 'report_type' ,
                'period_start' , 'period_end'
            )
        }) ,
        ('Content' , {
            'fields': (
                'executive_summary' , 'program_highlights' ,
                'kpi_updates' , 'challenges' ,
                'financial_summary' , 'recommendations'
            )
        }) ,
        ('Review Process' , {
            'fields': (
                'prepared_by' , 'reviewed_by' ,
                'status' , 'report_file'
            )
        })
    )

    def period_display(self , obj):
        return f"{obj.period_start} to {obj.period_end}"

    period_display.short_description = 'Period'

    def review_status(self , obj):
        status_colors = {
            'DRAFT': 'blue' ,
            'REVIEW': 'orange' ,
            'APPROVED': 'green' ,
            'PUBLISHED': 'purple'
        }
        return format_html(
            '<span style="color: {};">{}</span>' ,
            status_colors[obj.status] ,
            obj.get_status_display()
        )

    review_status.short_description = 'Review Status'

    def save_model(self , request , obj , form , change):
        if not change:  # If creating new object
            obj.prepared_by = request.user.member
        super().save_model(request , obj , form , change)


@admin.register(EmploymentTracking)
class EmploymentTrackingAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'participant_name' , 'initiative' , 'status' ,
        'employer_name' , 'position' , 'placement_date' ,
        'retention_period_display'
    )
    list_filter = (
        'status' , 'placement_date' , 'is_field_related' ,
        'initiative'
    )
    search_fields = (
        'participant__user__first_name' , 'participant__user__last_name' ,
        'employer_name' , 'position' , 'skills_utilized'
    )

    fieldsets = (
        ('Basic Information' , {
            'fields': (
                'participant' , 'initiative' , 'status' ,
                'is_field_related'
            )
        }) ,
        ('Employment Details' , {
            'fields': (
                'employer_name' , 'position' , 'salary_range' ,
                'placement_date' , 'retention_period'
            )
        }) ,
        ('Skills & Feedback' , {
            'fields': (
                'skills_utilized' , 'feedback_from_employer'
            ) ,
            'classes': ('collapse' ,)
        })
    )

    def participant_name(self , obj):
        return obj.participant.user.get_full_name()

    participant_name.short_description = 'Participant'

    def retention_period_display(self , obj):
        if not obj.retention_period:
            return '-'
        if obj.retention_period >= 12:
            return format_html(
                '<span style="color: green;">{} months</span>' ,
                obj.retention_period
            )
        return format_html(
            '<span style="color: orange;">{} months</span>' ,
            obj.retention_period
        )

    retention_period_display.short_description = 'Retention'


@admin.register(SkillAssessment)
class SkillAssessmentAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'participant_name' , 'initiative' , 'assessment_type' ,
        'assessment_date' , 'confidence_score_display' ,
        'evaluator_name'
    )
    list_filter = (
        'assessment_type' , 'assessment_date' ,
        'confidence_score' , 'initiative'
    )
    search_fields = (
        'participant__user__first_name' , 'participant__user__last_name' ,
        'recommendations' , 'improvement_areas'
    )

    fieldsets = (
        ('Basic Information' , {
            'fields': (
                'participant' , 'initiative' , 'assessment_type' ,
                'assessment_date' , 'evaluator'
            )
        }) ,
        ('Skills Assessment' , {
            'fields': (
                'technical_skills' , 'soft_skills' ,
                'confidence_score'
            )
        }) ,
        ('Feedback' , {
            'fields': (
                'recommendations' , 'improvement_areas'
            )
        })
    )

    def participant_name(self , obj):
        return obj.participant.user.get_full_name()

    participant_name.short_description = 'Participant'

    def evaluator_name(self , obj):
        if obj.evaluator:
            return obj.evaluator.user.get_full_name()
        return '-'

    evaluator_name.short_description = 'Evaluator'

    def confidence_score_display(self , obj):
        colors = {
            1: 'red' ,
            2: 'orange' ,
            3: 'yellow' ,
            4: 'lightgreen' ,
            5: 'green'
        }
        return format_html(
            '<span style="color: {};">★</span> ' * obj.confidence_score ,
            colors[obj.confidence_score]
        )

    confidence_score_display.short_description = 'Confidence'


@admin.register(WeeklyProgress)
class WeeklyProgressAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'initiative' , 'week_display' , 'status' ,
        'completion_rate' , 'bottleneck_indicator' ,
        'recorded_by_name'
    )
    list_filter = ('status' , 'week_start_date' , 'initiative')
    search_fields = (
        'planned_activities' , 'completed_activities' ,
        'bottlenecks' , 'initiative__name'
    )
    filter_horizontal = ('team_members' ,)

    fieldsets = (
        ('Basic Information' , {
            'fields': (
                'initiative' , 'week_start_date' , 'week_end_date' ,
                'status'
            )
        }) ,
        ('Activities' , {
            'fields': (
                'planned_activities' , 'completed_activities' ,
                'next_week_plan'
            )
        }) ,
        ('Issues & Support' , {
            'fields': (
                'bottlenecks' , 'mitigation_steps' ,
                'support_needed'
            )
        }) ,
        ('Team & Documentation' , {
            'fields': (
                'recorded_by' , 'team_members' ,
                'attachments'
            )
        })
    )

    def week_display(self , obj):
        return f"{obj.week_start_date.strftime('%d %b')} - {obj.week_end_date.strftime('%d %b %Y')}"

    week_display.short_description = 'Week Period'

    def completion_rate(self , obj):
        completed = len(obj.completed_activities.split('\n'))
        planned = len(obj.planned_activities.split('\n'))
        if planned == 0:
            return '0%'
        percentage = (completed / planned) * 100
        color = 'green' if percentage >= 75 else 'orange' if percentage >= 50 else 'red'
        return format_html(
            '<div style="width:100px; background-color: #f8f9fa;">'
            '<div style="width: {}px; background-color: {}; height: 20px;"></div>'
            '<span style="color: black;">{:.1f}%</span></div>' ,
            percentage ,
            color ,
            percentage
        )

    completion_rate.short_description = 'Completion'

    def bottleneck_indicator(self , obj):
        if not obj.bottlenecks:
            return format_html('<span style="color: green;">✓</span>')
        return format_html(
            '<span style="color: red;" title="{}">{}</span>' ,
            obj.bottlenecks[:100] + '...' if len(obj.bottlenecks) > 100 else obj.bottlenecks ,
            '⚠'
        )

    bottleneck_indicator.short_description = 'Issues'

    def recorded_by_name(self , obj):
        return obj.recorded_by.user.get_full_name()

    recorded_by_name.short_description = 'Recorded By'


@admin.register(QuarterlyImpactReview)
class QuarterlyImpactReviewAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'initiative' , 'quarter_display' , 'impact_metrics_display' ,
        'financial_metrics_display' , 'prepared_by_name' ,
        'status_display'
    )
    list_filter = ('year' , 'quarter' , 'initiative')
    search_fields = (
        'key_achievements' , 'challenges_faced' ,
        'recommendations' , 'initiative__name'
    )

    fieldsets = (
        ('Review Period' , {
            'fields': (
                'initiative' , 'year' , 'quarter' ,
                'start_date' , 'end_date'
            )
        }) ,
        ('Impact Metrics' , {
            'fields': (
                'total_beneficiaries' , 'skill_completion_rate' ,
                'employment_rate' , 'avg_confidence_score'
            )
        }) ,
        ('Financial Metrics' , {
            'fields': (
                'budget_utilized' , 'cost_per_beneficiary'
            )
        }) ,
        ('Analysis' , {
            'fields': (
                'key_achievements' , 'challenges_faced' ,
                'lessons_learned' , 'recommendations'
            )
        }) ,
        ('Planning' , {
            'fields': ('next_quarter_focus' ,)
        }) ,
        ('Review Process' , {
            'fields': (
                'prepared_by' , 'reviewed_by' ,
                'presentation_file'
            )
        })
    )

    def quarter_display(self , obj):
        return f"Q{obj.quarter} {obj.year}"

    quarter_display.short_description = 'Quarter'

    def impact_metrics_display(self , obj):
        return format_html(
            'Beneficiaries: {}<br>'
            'Skills: {:.1f}%<br>'
            'Employment: {:.1f}%' ,
            obj.total_beneficiaries ,
            obj.skill_completion_rate ,
            obj.employment_rate
        )

    impact_metrics_display.short_description = 'Impact Metrics'

    def financial_metrics_display(self , obj):
        return format_html(
            'Budget: ${:,.2f}<br>'
            'Cost/Beneficiary: ${:,.2f}' ,
            obj.budget_utilized ,
            obj.cost_per_beneficiary
        )

    financial_metrics_display.short_description = 'Financial Metrics'

    def prepared_by_name(self , obj):
        return obj.prepared_by.user.get_full_name()

    prepared_by_name.short_description = 'Prepared By'

    def status_display(self , obj):
        if obj.reviewed_by:
            return format_html(
                '<span style="color: green;">Reviewed by {}</span>' ,
                obj.reviewed_by.user.get_full_name()
            )
        return format_html(
            '<span style="color: orange;">Pending Review</span>'
        )

    status_display.short_description = 'Status'


@admin.register(FinancialTracking)
class FinancialTrackingAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'initiative' , 'month' , 'category' ,
        'amount_comparison' , 'variance_display' ,
        'recorded_by_name' , 'approval_status'
    )
    list_filter = (
        'category' , 'month' , 'initiative' ,
        ('approved_by' , admin.RelatedOnlyFieldListFilter)
    )
    search_fields = (
        'description' , 'variance_notes' ,
        'initiative__name'
    )

    fieldsets = (
        ('Basic Information' , {
            'fields': (
                'initiative' , 'month' , 'category' ,
                'description'
            )
        }) ,
        ('Financial Details' , {
            'fields': (
                'budgeted_amount' , 'actual_amount' ,
                'variance_notes'
            )
        }) ,
        ('Documentation' , {
            'fields': (
                'bills_attachment' , 'recorded_by' ,
                'approved_by'
            )
        })
    )

    def amount_comparison(self , obj):
        return format_html(
            'Budget: ${:,.2f}<br>'
            'Actual: ${:,.2f}' ,
            obj.budgeted_amount ,
            obj.actual_amount
        )

    amount_comparison.short_description = 'Amount'

    def variance_display(self , obj):
        variance = obj.variance_percentage()
        color = 'red' if variance > 10 else 'green' if variance < 0 else 'orange'
        return format_html(
            '<span style="color: {};">{:+.1f}%<br>(${:,.2f})</span>' ,
            color ,
            variance ,
            obj.variance_amount()
        )

    variance_display.short_description = 'Variance'

    def recorded_by_name(self , obj):
        return obj.recorded_by.user.get_full_name()

    recorded_by_name.short_description = 'Recorded By'

    def approval_status(self , obj):
        if obj.approved_by:
            return format_html(
                '<span style="color: green;">✓ Approved</span>'
            )
        return format_html(
            '<span style="color: orange;">Pending</span>'
        )

    approval_status.short_description = 'Approval'

    def save_model(self , request , obj , form , change):
        if not change:  # If creating new object
            obj.recorded_by = request.user.member
        super().save_model(request , obj , form , change)

# Register any additional customizations here
admin.site.site_header = 'MCSU Monitoring & Evaluation Administration'
admin.site.site_title = 'MCSU M&E'
admin.site.index_title = 'Monitoring & Evaluation Management'