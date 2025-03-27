# program_design/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    DiversityMetric, CoCreationWorkshop, InclusionTraining,
    CulturalSensitivityAudit, ProgramFeedback
)

@admin.register(DiversityMetric)
class DiversityMetricAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'initiative', 'date_recorded', 'total_participants',
        'women_percentage_display', 'lgbtqia_percentage_display',
        'marginalized_percentage_display'
    )
    list_filter = ('date_recorded', 'initiative')
    search_fields = ('initiative__name', 'notes')
    readonly_fields = ('date_recorded',)

    def women_percentage_display(self, obj):
        percentage = obj.women_percentage()
        return self.get_percentage_display(percentage)
    women_percentage_display.short_description = 'Women %'

    def lgbtqia_percentage_display(self, obj):
        percentage = obj.lgbtqia_percentage()
        return self.get_percentage_display(percentage)
    lgbtqia_percentage_display.short_description = 'LGBTQIA+ %'

    def marginalized_percentage_display(self, obj):
        percentage = obj.marginalized_percentage()
        return self.get_percentage_display(percentage)
    marginalized_percentage_display.short_description = 'Marginalized %'

    def get_percentage_display(self, percentage):
        color = 'green' if percentage >= 30 else 'orange' if percentage >= 20 else 'red'
        return format_html(
            '<span style="color: {};">{:.1f}%</span>',
            color,
            percentage
        )

@admin.register(CoCreationWorkshop)
class CoCreationWorkshopAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'title', 'initiative', 'date', 'status',
        'facilitator', 'participant_breakdown'
    )
    list_filter = ('status', 'date')
    search_fields = ('title', 'initiative__name', 'agenda')
    readonly_fields = ('created_at', 'updated_at')

    def participant_breakdown(self, obj):
        return format_html(
            'Total: {} (W: {}, L: {}, M: {})',
            obj.total_participants,
            obj.women_count,
            obj.lgbtqia_count,
            obj.marginalized_count
        )
    participant_breakdown.short_description = 'Participants'

@admin.register(InclusionTraining)
class InclusionTrainingAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'title', 'training_type', 'start_date',
        'status', 'facilitator', 'participant_count'
    )
    list_filter = ('training_type', 'status', 'start_date')
    search_fields = ('title', 'description', 'objectives')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('participants',)

    def participant_count(self, obj):
        count = obj.participants.count()
        return format_html('{} participants', count)
    participant_count.short_description = 'Participants'

@admin.register(CulturalSensitivityAudit)
class CulturalSensitivityAuditAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'initiative', 'audit_type', 'audit_date',
        'auditor', 'completion_status', 'follow_up_status'
    )
    list_filter = ('audit_type', 'completion_status', 'audit_date')
    search_fields = ('initiative__name', 'findings', 'recommendations')
    readonly_fields = ('created_at',)

    def follow_up_status(self, obj):
        if obj.completion_status:
            return format_html('<span style="color: green;">Completed</span>')
        days_remaining = (obj.follow_up_date - timezone.now().date()).days
        color = 'green' if days_remaining > 7 else 'orange' if days_remaining > 0 else 'red'
        return format_html(
            '<span style="color: {};">{} days remaining</span>',
            color,
            days_remaining
        )
    follow_up_status.short_description = 'Follow-up Status'

@admin.register(ProgramFeedback)
class ProgramFeedbackAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'initiative', 'category', 'feedback_summary',
        'satisfaction_status', 'submitted_at'
    )
    list_filter = (
        'category', 'expectations_met',
        'culturally_sensitive', 'submitted_at'
    )
    search_fields = (
        'feedback_text', 'improvement_suggestions',
        'initiative__name'
    )
    readonly_fields = ('submitted_at',)

    def feedback_summary(self, obj):
        return format_html(
            '<span title="{}">{}</span>',
            obj.feedback_text,
            obj.feedback_text[:50] + '...' if len(obj.feedback_text) > 50 else obj.feedback_text
        )
    feedback_summary.short_description = 'Feedback'

    def satisfaction_status(self, obj):
        if obj.expectations_met and obj.culturally_sensitive:
            return format_html('<span style="color: green;">✓ Satisfied</span>')
        elif not obj.expectations_met and not obj.culturally_sensitive:
            return format_html('<span style="color: red;">✗ Unsatisfied</span>')
        return format_html('<span style="color: orange;">◐ Partially Satisfied</span>')
    satisfaction_status.short_description = 'Satisfaction'

# Register any additional admin customizations here
admin.site.site_header = 'MCSU Program Design Administration'
admin.site.site_title = 'MCSU Program Design'
admin.site.index_title = 'Program Design Management'