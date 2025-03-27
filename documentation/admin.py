# documentation/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    ProgramLogbook , DocumentTemplate , ImpactStory , CSRReport
)
from .models import (
    ProgressReport, SDGMapping, SDGProgress,
    ReportDistribution, DocumentationReview
)


@admin.register(ProgramLogbook)
class ProgramLogbookAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'initiative' , 'date' , 'activity_type' ,
        'participants_display' , 'milestone_indicator' ,
        'challenges_indicator' , 'recorded_by_name'
    )
    list_filter = (
        'activity_type' , 'date' , 'initiative' ,
        ('recorded_by' , admin.RelatedOnlyFieldListFilter)
    )
    search_fields = (
        'activity_description' , 'milestone_reached' ,
        'challenges_faced' , 'next_steps'
    )

    fieldsets = (
        ('Basic Information' , {
            'fields': (
                'initiative' , 'date' , 'activity_type' ,
                'activity_description'
            )
        }) ,
        ('Participation' , {
            'fields': ('participants_count' ,)
        }) ,
        ('Progress & Challenges' , {
            'fields': (
                'milestone_reached' , 'challenges_faced' ,
                'next_steps'
            )
        }) ,
        ('Documentation' , {
            'fields': ('recorded_by' , 'attachments')
        })
    )

    def participants_display(self , obj):
        if obj.participants_count == 0:
            return '-'
        return format_html(
            '<span style="color: {};">{} participants</span>' ,
            'green' if obj.participants_count >= 10 else 'orange' ,
            obj.participants_count
        )

    participants_display.short_description = 'Participation'

    def milestone_indicator(self , obj):
        if obj.milestone_reached:
            return format_html(
                '<span title="{}" style="color: green;">✓</span>' ,
                obj.milestone_reached
            )
        return format_html(
            '<span style="color: orange;">-</span>'
        )

    milestone_indicator.short_description = 'Milestone'

    def challenges_indicator(self , obj):
        if obj.challenges_faced:
            return format_html(
                '<span title="{}" style="color: red;">⚠</span>' ,
                obj.challenges_faced
            )
        return format_html(
            '<span style="color: green;">✓</span>'
        )

    challenges_indicator.short_description = 'Challenges'

    def recorded_by_name(self , obj):
        return obj.recorded_by.user.get_full_name()

    recorded_by_name.short_description = 'Recorded By'
    
    def has_view_permission(self, request, obj = ...):
        return False

@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'name' , 'template_type' , 'version' ,
        'status_display' , 'created_by_name' ,
        'last_updated'
    )
    list_filter = (
        'template_type' , 'is_active' , 'version' ,
        ('created_by' , admin.RelatedOnlyFieldListFilter)
    )
    search_fields = ('name' , 'description')

    fieldsets = (
        ('Basic Information' , {
            'fields': (
                'name' , 'template_type' , 'description' ,
                'is_active'
            )
        }) ,
        ('Template Details' , {
            'fields': (
                'template_content' , 'version'
            )
        }) ,
        ('Ownership' , {
            'fields': ('created_by' ,)
        })
    )

    def status_display(self , obj):
        if obj.is_active:
            return format_html(
                '<span style="color: green;">Active v{}</span>' ,
                obj.version
            )
        return format_html(
            '<span style="color: red;">Inactive v{}</span>' ,
            obj.version
        )

    status_display.short_description = 'Status'

    def created_by_name(self , obj):
        return obj.created_by.user.get_full_name()

    created_by_name.short_description = 'Created By'

    def last_updated(self , obj):
        return obj.updated_at.strftime("%Y-%m-%d %H:%M")

    last_updated.short_description = 'Last Updated'
    def has_view_permission(self, request, obj = ...):
        return False

@admin.register(ImpactStory)
class ImpactStoryAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'title' , 'initiative' , 'story_type' ,
        'participant_display' , 'sdg_alignment' ,
        'approval_status_display'
    )
    list_filter = (
        'story_type' , 'sdg_alignment' , 'approval_status' ,
        'is_anonymous' , 'initiative'
    )
    search_fields = (
        'title' , 'participant_name' , 'challenge_description' ,
        'testimonial'
    )

    fieldsets = (
        ('Basic Information' , {
            'fields': (
                'initiative' , 'title' , 'story_type' ,
                'sdg_alignment'
            )
        }) ,
        ('Participant Details' , {
            'fields': (
                'participant_name' , 'is_anonymous'
            )
        }) ,
        ('Story Content' , {
            'fields': (
                'challenge_description' , 'solution_provided' ,
                'outcome' , 'testimonial'
            )
        }) ,
        ('Impact Metrics' , {
            'fields': ('metrics_achieved' ,)
        }) ,
        ('Media & Documentation' , {
            'fields': ('media_attachments' ,)
        }) ,
        ('Approval Process' , {
            'fields': (
                'approval_status' , 'collected_by' ,
                'approved_by'
            )
        })
    )

    def participant_display(self , obj):
        if obj.is_anonymous:
            return format_html(
                '<span style="color: gray;">Anonymous</span>'
            )
        return obj.participant_name

    participant_display.short_description = 'Participant'

    def approval_status_display(self , obj):
        status_colors = {
            'DRAFT': 'gray' ,
            'REVIEW': 'orange' ,
            'APPROVED': 'green' ,
            'PUBLISHED': 'blue'
        }
        return format_html(
            '<span style="color: {};">{}</span>' ,
            status_colors[obj.approval_status] ,
            obj.get_approval_status_display()
        )

    approval_status_display.short_description = 'Status'


@admin.register(CSRReport)
class CSRReportAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'initiative' , 'report_type' , 'period_display' ,
        'sdg_metrics_summary' , 'financial_summary' ,
        'status_display'
    )
    list_filter = (
        'report_type' , 'status' , 'period_start' ,
        'initiative'
    )
    search_fields = (
        'executive_summary' , 'program_highlights' ,
        'beneficiary_impact'
    )
    filter_horizontal = ('featured_stories' ,)

    fieldsets = (
        ('Report Information' , {
            'fields': (
                'initiative' , 'report_type' ,
                'period_start' , 'period_end'
            )
        }) ,
        ('SDG Metrics' , {
            'fields': ('sdg5_metrics' , 'sdg8_metrics')
        }) ,
        ('Report Content' , {
            'fields': (
                'executive_summary' , 'program_highlights' ,
                'beneficiary_impact' , 'sdg_alignment_narrative' ,
                'challenges_learnings' , 'future_plans'
            )
        }) ,
        ('Impact Stories' , {
            'fields': ('featured_stories' ,)
        }) ,
        ('Financial Information' , {
            'fields': (
                'budget_utilized' , 'cost_per_beneficiary' ,
                'dashboard_link'
            )
        }) ,
        ('Report Status' , {
            'fields': (
                'status' , 'prepared_by' , 'reviewed_by' ,
                'report_file'
            )
        }) ,
        ('Feedback' , {
            'fields': ('stakeholder_feedback' ,) ,
            'classes': ('collapse' ,)
        })
    )

    def period_display(self , obj):
        return f"{obj.period_start} to {obj.period_end}"

    period_display.short_description = 'Period'

    def sdg_metrics_summary(self , obj):
        metrics = obj.get_sdg_metrics_display()
        return format_html(
            'SDG 5: {} metrics<br>'
            'SDG 8: {} metrics' ,
            len(metrics['SDG 5']) ,
            len(metrics['SDG 8'])
        )

    sdg_metrics_summary.short_description = 'SDG Metrics'

    def financial_summary(self , obj):
        return format_html(
            'Budget: ${:,.2f}<br>'
            'Cost/Ben: ${:,.2f}' ,
            obj.budget_utilized ,
            obj.cost_per_beneficiary
        )

    financial_summary.short_description = 'Financial Summary'

    def status_display(self , obj):
        status_colors = {
            'DRAFT': 'gray' ,
            'REVIEW': 'orange' ,
            'APPROVED': 'green' ,
            'PUBLISHED': 'blue'
        }
        return format_html(
            '<span style="color: {};">{}</span>' ,
            status_colors[obj.status] ,
            obj.get_status_display()
        )

    status_display.short_description = 'Status'

    def save_model(self , request , obj , form , change):
        if not change:  # If creating new object
            obj.prepared_by = request.user.member
        super().save_model(request , obj , form , change)


class SDGProgressInline(admin.TabularInline):
    def has_module_permission(self, request):
        return False
    model = SDGProgress
    extra = 1
    fields = ('record_date' , 'value' , 'evidence' , 'recorded_by' , 'notes')
    readonly_fields = ('created_at' ,)


@admin.register(ProgressReport)
class ProgressReportAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'initiative' , 'reporting_period' , 'period_display' ,
        'status_badge' , 'prepared_by_name' , 'review_status'
    )
    list_filter = (
        'reporting_period' , 'status' , 'period_start' ,
        'initiative'
    )
    search_fields = (
        'executive_summary' , 'achievements' ,
        'challenges' , 'next_steps'
    )

    fieldsets = (
        ('Report Information' , {
            'fields': (
                'initiative' , 'reporting_period' ,
                'period_start' , 'period_end'
            )
        }) ,
        ('Report Content' , {
            'fields': (
                'executive_summary' , 'achievements' ,
                'challenges' , 'kpi_updates'
            )
        }) ,
        ('Financial & Next Steps' , {
            'fields': (
                'financial_summary' , 'next_steps'
            )
        }) ,
        ('Review Process' , {
            'fields': (
                'prepared_by' , 'reviewed_by' ,
                'review_comments' , 'status'
            )
        }) ,
        ('Documentation' , {
            'fields': ('report_file' ,) ,
            'classes': ('collapse' ,)
        })
    )

    def period_display(self , obj):
        return f"{obj.period_start} to {obj.period_end}"

    period_display.short_description = 'Period'

    def status_badge(self , obj):
        colors = {
            'DRAFT': 'gray' ,
            'SUBMITTED': 'blue' ,
            'REVIEWED': 'orange' ,
            'APPROVED': 'green'
        }
        return format_html(
            '<span style="color: {};">{}</span>' ,
            colors[obj.status] ,
            obj.get_status_display()
        )

    status_badge.short_description = 'Status'

    def prepared_by_name(self , obj):
        return obj.prepared_by.user.get_full_name()

    prepared_by_name.short_description = 'Prepared By'

    def review_status(self , obj):
        if obj.reviewed_by:
            return format_html(
                '<span style="color: green;">Reviewed by {}</span>' ,
                obj.reviewed_by.user.get_full_name()
            )
        return format_html(
            '<span style="color: orange;">Pending Review</span>'
        )

    review_status.short_description = 'Review Status'


@admin.register(SDGMapping)
class SDGMappingAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'initiative' , 'sdg' , 'progress_display' ,
        'measurement_frequency' , 'responsible_person'
    )
    list_filter = (
        'sdg' , 'collection_frequency' , 'initiative'
    )
    search_fields = (
        'program_outcome' , 'impact_area' ,
        'measurement_method'
    )
    inlines = [SDGProgressInline]

    fieldsets = (
        ('Basic Information' , {
            'fields': (
                'initiative' , 'sdg' , 'program_outcome' ,
                'impact_area'
            )
        }) ,
        ('Metrics & Targets' , {
            'fields': (
                'metrics' , 'baseline_value' ,
                'target_value' , 'current_value'
            )
        }) ,
        ('Measurement' , {
            'fields': (
                'measurement_method' , 'data_source' ,
                'collection_frequency'
            )
        }) ,
        ('Responsibility' , {
            'fields': (
                'responsible_person' , 'notes'
            )
        })
    )

    def progress_display(self , obj):
        percentage = obj.progress_percentage()
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

    def measurement_frequency(self , obj):
        return format_html(
            '<span style="color: blue;">{}</span>' ,
            obj.get_collection_frequency_display()
        )

    measurement_frequency.short_description = 'Frequency'



# documentation/admin.py

@admin.register(SDGProgress)
class SDGProgressAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'sdg_mapping_display' , 'record_date' ,
        'value_display' , 'recorded_by_name' ,
        'has_documents'
    )
    list_filter = (
        'record_date' ,
        'sdg_mapping__sdg' ,  # Removed RelatedOnlyFieldListFilter
        'recorded_by'
    )
    search_fields = (
        'evidence' ,
        'notes' ,
        'sdg_mapping__initiative__name'  # Added to search by initiative name
    )

    fieldsets = (
        ('Progress Information' , {
            'fields': (
                'sdg_mapping' , 'record_date' ,
                'value' , 'evidence'
            )
        }) ,
        ('Documentation' , {
            'fields': (
                'supporting_documents' , 'notes' ,
                'recorded_by'
            )
        })
    )

    def sdg_mapping_display(self , obj):
        return f"{obj.sdg_mapping.get_sdg_display()} - {obj.sdg_mapping.initiative.name}"

    sdg_mapping_display.short_description = 'SDG Mapping'

    def value_display(self , obj):
        target = obj.sdg_mapping.target_value
        percentage = (obj.value / target * 100) if target > 0 else 0
        color = 'green' if percentage >= 100 else 'orange' if percentage >= 75 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f} ({:.1f}%)</span>' ,
            color ,
            obj.value ,
            percentage
        )

    value_display.short_description = 'Value'

    def recorded_by_name(self , obj):
        return obj.recorded_by.user.get_full_name()

    recorded_by_name.short_description = 'Recorded By'

    def has_documents(self , obj):
        return bool(obj.supporting_documents)

    has_documents.boolean = True
    has_documents.short_description = 'Documents'

    def get_queryset(self , request):
        return super().get_queryset(request).select_related(
            'sdg_mapping' ,
            'sdg_mapping__initiative' ,
            'recorded_by' ,
            'recorded_by__user'
        )


@admin.register(ReportDistribution)
class ReportDistributionAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'report_type' , 'distribution_date' ,
        'distribution_method' , 'distributed_by_name' ,
        'acknowledgment_status' , 'follow_up_status'
    )
    list_filter = (
        'report_type' , 'distribution_method' ,
        'distribution_date' , 'acknowledgment_status' ,
        'follow_up_required'
    )
    search_fields = ('recipients' , 'feedback_received' , 'follow_up_notes')

    fieldsets = (
        ('Distribution Information' , {
            'fields': (
                'report_type' , 'content_type' , 'object_id' ,
                'distribution_date' , 'distribution_method'
            )
        }) ,
        ('Recipients & Status' , {
            'fields': (
                'recipients' , 'distributed_by' ,
                'acknowledgment_status'
            )
        }) ,
        ('Feedback & Follow-up' , {
            'fields': (
                'feedback_received' , 'follow_up_required' ,
                'follow_up_notes'
            )
        })
    )

    def distributed_by_name(self , obj):
        return obj.distributed_by.user.get_full_name()

    distributed_by_name.short_description = 'Distributed By'

    def follow_up_status(self , obj):
        if not obj.follow_up_required:
            return format_html('<span style="color: green;">No Follow-up Needed</span>')
        return format_html(
            '<span style="color: red;">Follow-up Required</span>'
        )

    follow_up_status.short_description = 'Follow-up'


@admin.register(DocumentationReview)
class DocumentationReviewAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'initiative' , 'review_type' , 'review_date' ,
        'reviewed_by_name' , 'status_display' ,
        'follow_up_countdown'
    )
    list_filter = (
        'review_type' , 'status' , 'review_date' ,
        'initiative'
    )
    search_fields = (
        'completeness_check' , 'quality_assessment' ,
        'identified_gaps' , 'recommendations'
    )

    fieldsets = (
        ('Review Information' , {
            'fields': (
                'initiative' , 'review_type' , 'review_date' ,
                'period_start' , 'period_end'
            )
        }) ,
        ('Assessment' , {
            'fields': (
                'completeness_check' , 'quality_assessment' ,
                'identified_gaps'
            )
        }) ,
        ('Action Plan' , {
            'fields': (
                'recommendations' , 'action_items' ,
                'follow_up_date'
            )
        }) ,
        ('Status' , {
            'fields': (
                'reviewed_by' , 'status'
            )
        })
    )

    def reviewed_by_name(self , obj):
        return obj.reviewed_by.user.get_full_name()

    reviewed_by_name.short_description = 'Reviewed By'

    def status_display(self , obj):
        colors = {
            'PENDING': 'red' ,
            'IN_PROGRESS': 'orange' ,
            'COMPLETED': 'green'
        }
        return format_html(
            '<span style="color: {};">{}</span>' ,
            colors[obj.status] ,
            obj.get_status_display()
        )

    status_display.short_description = 'Status'

    def follow_up_countdown(self , obj):
        if obj.status == 'COMPLETED':
            return '-'
        days = (obj.follow_up_date - timezone.now().date()).days
        color = 'green' if days > 7 else 'orange' if days > 0 else 'red'
        return format_html(
            '<span style="color: {};">{} days</span>' ,
            color ,
            days
        )

    follow_up_countdown.short_description = 'Follow-up In'

    def save_model(self , request , obj , form , change):
        if not obj.reviewed_by:
            obj.reviewed_by = request.user.member
        super().save_model(request , obj , form , change)

# Custom admin site configuration
admin.site.site_header = 'MCSU Documentation Management'
admin.site.site_title = 'MCSU Documentation'
admin.site.index_title = 'Documentation Management System'