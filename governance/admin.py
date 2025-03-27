# governance/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    TeamRole , ResourceAllocation , ProjectTimeline , RiskAssessment ,
    GovernanceBody , GovernanceMeeting , CSRProposal , GovernanceReport
)


@admin.register(TeamRole)
class TeamRoleAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'member_name' , 'role_type' , 'status_display' ,
        'initiatives_count' , 'reporting_to_display'
    )
    list_filter = ('role_type' , 'is_active' , 'start_date')
    search_fields = ('member__user__first_name' , 'member__user__last_name' , 'responsibilities')
    filter_horizontal = ('initiatives' ,)

    fieldsets = (
        ('Basic Information' , {
            'fields': ('member' , 'role_type' , 'is_active' , 'reporting_to')
        }) ,
        ('Timeline' , {
            'fields': ('start_date' , 'end_date')
        }) ,
        ('Role Details' , {
            'fields': ('responsibilities' , 'tools_used' , 'initiatives')
        })
    )

    def member_name(self , obj):
        return obj.member.user.get_full_name()

    member_name.short_description = 'Member'

    def status_display(self , obj):
        if obj.is_active:
            return format_html(
                '<span style="color: green;">Active</span>'
            )
        return format_html(
            '<span style="color: red;">Inactive</span>'
        )

    status_display.short_description = 'Status'

    def initiatives_count(self , obj):
        count = obj.initiatives.count()
        return format_html(
            '<a href="{}?team_members__id={}">{} initiatives</a>' ,
            reverse('admin:initiatives_initiative_changelist') ,
            obj.id ,
            count
        )

    initiatives_count.short_description = 'Initiatives'

    def reporting_to_display(self , obj):
        if obj.reporting_to:
            return f"{obj.reporting_to.member.user.get_full_name()} ({obj.reporting_to.get_role_type_display()})"
        return "No manager"

    reporting_to_display.short_description = 'Reports To'


@admin.register(ResourceAllocation)
class ResourceAllocationAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'initiative' , 'resource_type' , 'status' ,
        'cost_display' , 'requested_by' , 'required_by_date'
    )
    list_filter = ('status' , 'resource_type' , 'requested_date')
    search_fields = ('initiative__name' , 'description' , 'requested_by__user__username')

    fieldsets = (
        ('Basic Information' , {
            'fields': ('initiative' , 'resource_type' , 'description')
        }) ,
        ('Cost Details' , {
            'fields': ('estimated_cost' , 'actual_cost' , 'quantity')
        }) ,
        ('Status' , {
            'fields': ('status' , 'requested_by' , 'approved_by')
        }) ,
        ('Timeline' , {
            'fields': ('required_by_date' , 'procurement_date')
        }) ,
        ('Additional Information' , {
            'fields': ('notes' ,) ,
            'classes': ('collapse' ,)
        })
    )

    def cost_display(self , obj):
        variance = obj.actual_cost - obj.estimated_cost
        color = 'red' if variance > 0 else 'green'
        return format_html(
            'Est: ${:,.2f}<br>Act: ${:,.2f}<br>'
            '<span style="color: {};">Var: ${:,.2f}</span>' ,
            obj.estimated_cost ,
            obj.actual_cost ,
            color ,
            abs(variance)
        )

    cost_display.short_description = 'Cost Details'


@admin.register(ProjectTimeline)
class ProjectTimelineAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'task_name' , 'initiative' , 'assigned_to' ,
        'status' , 'priority' , 'progress_display' ,
        'timeline_status'
    )
    list_filter = ('status' , 'priority' , 'start_date')
    search_fields = ('task_name' , 'description' , 'initiative__name')
    filter_horizontal = ('dependencies' ,)

    fieldsets = (
        ('Basic Information' , {
            'fields': ('initiative' , 'task_name' , 'description')
        }) ,
        ('Assignment' , {
            'fields': ('assigned_to' , 'priority' , 'status')
        }) ,
        ('Timeline' , {
            'fields': ('start_date' , 'end_date' , 'progress')
        }) ,
        ('Dependencies' , {
            'fields': ('dependencies' , 'tool_link')
        }) ,
        ('Additional Information' , {
            'fields': ('notes' ,) ,
            'classes': ('collapse' ,)
        })
    )

    def get_tasks(self , obj):
        return obj.governance_assigned_tasks.count()

    def progress_display(self , obj):
        color = 'green' if obj.progress >= 75 else 'orange' if obj.progress >= 50 else 'red'
        return format_html(
            '<div style="width:100px; background-color: #f8f9fa;">'
            '<div style="width: {}px; background-color: {}; height: 20px;"></div>'
            '<span style="color: black;">{}</span></div>' ,
            obj.progress ,
            color ,
            f"{obj.progress}%"
        )

    progress_display.short_description = 'Progress'

    def timeline_status(self , obj):
        if obj.status == 'COMPLETED':
            return format_html('<span style="color: green;">Completed</span>')

        today = timezone.now().date()
        if obj.end_date < today:
            days_overdue = (today - obj.end_date).days
            return format_html(
                '<span style="color: red;">{} days overdue</span>' ,
                days_overdue
            )

        days_remaining = (obj.end_date - today).days
        return format_html(
            '<span style="color: green;">{} days remaining</span>' ,
            days_remaining
        )

    timeline_status.short_description = 'Timeline'


@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'initiative' , 'risk_type' , 'status' ,
        'risk_level_display' , 'assigned_to' ,
        'next_review_date'
    )
    list_filter = ('risk_type' , 'status' , 'likelihood' , 'impact')
    search_fields = ('description' , 'initiative__name' , 'mitigation_plan')

    fieldsets = (
        ('Risk Information' , {
            'fields': ('initiative' , 'risk_type' , 'description')
        }) ,
        ('Assessment' , {
            'fields': ('likelihood' , 'impact' , 'status')
        }) ,
        ('Assignment' , {
            'fields': ('identified_by' , 'assigned_to')
        }) ,
        ('Review Dates' , {
            'fields': ('next_review_date' , 'resolution_date')
        }) ,
        ('Plans' , {
            'fields': ('mitigation_plan' , 'contingency_plan' , 'fallback_strategy')
        }) ,
        ('Outcome' , {
            'fields': ('actual_impact' , 'lessons_learned') ,
            'classes': ('collapse' ,)
        }) ,
        ('Documentation' , {
            'fields': ('attachments' ,) ,
            'classes': ('collapse' ,)
        })
    )

    def risk_level_display(self , obj):
        risk_score = obj.risk_score()
        if risk_score >= 6:
            color = 'red'
            level = 'High'
        elif risk_score >= 3:
            color = 'orange'
            level = 'Medium'
        else:
            color = 'green'
            level = 'Low'

        return format_html(
            '<span style="color: {};">{} (Score: {})</span>' ,
            color ,
            level ,
            risk_score
        )

    risk_level_display.short_description = 'Risk Level'


@admin.register(GovernanceBody)
class GovernanceBodyAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'name' , 'committee_type' , 'chairperson' ,
        'members_count' , 'meeting_frequency' ,
        'status_display'
    )
    list_filter = ('committee_type' , 'is_active' , 'meeting_frequency')
    search_fields = ('name' , 'description' , 'terms_of_reference')
    filter_horizontal = ('members' ,)

    fieldsets = (
        ('Basic Information' , {
            'fields': ('name' , 'committee_type' , 'description')
        }) ,
        ('Leadership' , {
            'fields': ('chairperson' , 'secretary' , 'members')
        }) ,
        ('Terms' , {
            'fields': ('formation_date' , 'tenure_end_date' , 'meeting_frequency')
        }) ,
        ('Requirements' , {
            'fields': ('quorum_requirement' , 'terms_of_reference')
        }) ,
        ('Status' , {
            'fields': ('is_active' ,)
        })
    )

    def members_count(self , obj):
        return obj.members.count()

    members_count.short_description = 'Members'

    def status_display(self , obj):
        if not obj.is_active:
            return format_html('<span style="color: red;">Inactive</span>')

        if obj.tenure_end_date < timezone.now().date():
            return format_html('<span style="color: orange;">Tenure Expired</span>')

        return format_html('<span style="color: green;">Active</span>')

    status_display.short_description = 'Status'


@admin.register(GovernanceMeeting)
class GovernanceMeetingAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'governance_body' , 'meeting_date' ,
        'attendees_count' , 'next_meeting_date'
    )
    list_filter = ('governance_body' , 'meeting_date')
    search_fields = ('agenda' , 'minutes' , 'decisions_made')
    filter_horizontal = ('attendees' ,)

    fieldsets = (
        ('Meeting Information' , {
            'fields': ('governance_body' , 'meeting_date' , 'next_meeting_date')
        }) ,
        ('Attendance' , {
            'fields': ('attendees' ,)
        }) ,
        ('Content' , {
            'fields': ('agenda' , 'minutes' , 'decisions_made' , 'action_items')
        }) ,
        ('Documentation' , {
            'fields': ('attachments' ,) ,
            'classes': ('collapse' ,)
        })
    )

    def attendees_count(self , obj):
        count = obj.attendees.count()
        total = obj.governance_body.members.count()
        return f"{count}/{total} members"

    attendees_count.short_description = 'Attendance'


@admin.register(CSRProposal)
class CSRProposalAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'title' , 'company_name' , 'status' ,
        'amount_display' , 'submission_deadline' ,
        'prepared_by'
    )
    list_filter = ('status' , 'submission_deadline')
    search_fields = ('title' , 'company_name' , 'executive_summary')

    fieldsets = (
        ('Basic Information' , {
            'fields': (
                'title' , 'initiative' , 'company_name' ,
                'submission_deadline'
            )
        }) ,
        ('Financial' , {
            'fields': ('requested_amount' , 'approved_amount')
        }) ,
        ('Status & Assignment' , {
            'fields': ('status' , 'prepared_by' , 'reviewed_by')
        }) ,
        ('Proposal Content' , {
            'fields': (
                'executive_summary' , 'alignment_with_sdgs' ,
                'budget_breakdown' , 'impact_metrics' ,
                'partnership_details'
            )
        }) ,
        ('Submission Details' , {
            'fields': (
                'submission_date' , 'feedback_received' ,
                'proposal_document'
            ) ,
            'classes': ('collapse' ,)
        })
    )

    def amount_display(self , obj):
        if obj.approved_amount:
            color = 'green' if obj.approved_amount >= obj.requested_amount else 'red'
            return format_html(
                'Requested: ${:,.2f}<br>'
                '<span style="color: {};">Approved: ${:,.2f}</span>' ,
                obj.requested_amount ,
                color ,
                obj.approved_amount
            )
        return format_html('Requested: ${:,.2f}' , obj.requested_amount)

    amount_display.short_description = 'Amount'


@admin.register(GovernanceReport)
class GovernanceReportAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = (
        'report_type' , 'period_display' , 'prepared_by' ,
        'submitted_date' , 'approval_status'
    )
    list_filter = ('report_type' , 'submitted_date')
    search_fields = (
        'executive_summary' , 'progress_overview' ,
        'challenges_risks'
    )

    fieldsets = (
        ('Report Information' , {
            'fields': (
                'report_type' , 'period_start' , 'period_end' ,
                'prepared_by'
            )
        }) ,
        ('Content' , {
            'fields': (
                'executive_summary' , 'progress_overview' ,
                'financial_overview' , 'challenges_risks' ,
                'recommendations'
            )
        }) ,
        ('Submission & Approval' , {
            'fields': (
                'submitted_date' , 'attachments' ,
                'approved_by' , 'approval_date'
            )
        })
    )

    def period_display(self , obj):
        return f"{obj.period_start} to {obj.period_end}"

    period_display.short_description = 'Period'

    def approval_status(self , obj):
        if obj.approved_by:
            return format_html(
                '<span style="color: green;">Approved by {} on {}</span>' ,
                obj.approved_by.user.get_full_name() ,
                obj.approval_date
            )
        return format_html(
            '<span style="color: orange;">Pending Approval</span>'
        )

    approval_status.short_description = 'Approval Status'


# Register any additional admin customizations here
admin.site.site_header = 'MCSU Governance Administration'
admin.site.site_title = 'MCSU Governance'
admin.site.index_title = 'Governance Management'