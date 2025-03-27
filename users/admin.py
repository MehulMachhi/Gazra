from django.contrib import admin
from django.utils.html import format_html
from django.utils.timezone import now
from django.http import HttpResponse
import csv
from datetime import datetime

from .models import Member, CoreCommittee, Department, StudentVolunteer

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'member_type', 'status', 'join_date', 'phone_number', 'last_active')
    list_filter = ('member_type', 'status', 'join_date')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'phone_number')
    raw_id_fields = ('user',)

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'user', 'member_type', 'status', 'join_date', 'bio', 'profile_picture'
            )
        }),
        ('Skills & Certifications', {
            'fields': ('skills', 'certifications')
        }),
        ('Professional Profiles', {
            'fields': ('linkedin_profile', 'github_profile')
        }),
        ('Contact Information', {
            'fields': (
                'phone_number', 'emergency_contact', 'emergency_phone'
            )
        })
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(CoreCommittee)
class CoreCommitteeAdmin(admin.ModelAdmin):
    list_display = ('member', 'role', 'term_start', 'term_end', 'is_active')
    list_filter = ('role', 'is_active', 'term_start', 'term_end')
    search_fields = ('member__user__first_name', 'member__user__last_name', 'role')
    raw_id_fields = ('member',)

    fieldsets = (
        ('Position Details', {
            'fields': (
                'member', 'role', 'is_active', 'term_start', 'term_end'
            )
        }),
        ('Role Information', {
            'fields': ('responsibilities', 'achievements', 'handover_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'head', 'is_active', 'budget_allocation', 'contact_email')
    list_filter = ('is_active', 'established_on')
    search_fields = ('name', 'description', 'contact_email')
    raw_id_fields = ('head',)

    fieldsets = (
        ('Department Details', {
            'fields': (
                'name', 'description', 'head', 'is_active', 'established_on'
            )
        }),
        ('Vision & Mission', {
            'fields': ('vision', 'mission')
        }),
        ('Financial & Contact', {
            'fields': ('budget_allocation', 'contact_email')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(StudentVolunteer)
class StudentVolunteerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'university_name', 'department', 'status', 'application_date')
    list_filter = ('status', 'sex', 'university_name', 'current_semester')
    search_fields = ('name', 'email', 'phone_no', 'university_name')
    raw_id_fields = ('department', 'event', 'initiative', 'approved_by')

    fieldsets = (
        ('Personal Information', {
            'fields': (
                'name', 'sex', 'email', 'phone_no', 'address'
            )
        }),
        ('Academic Details', {
            'fields': (
                'university_name', 'current_semester', 'university_permission'
            )
        }),
        ('Volunteer Assignment', {
            'fields': (
                'department', 'event', 'initiative', 'work_duration_months'
            )
        }),
        ('Skills & Availability', {
            'fields': (
                'skills', 'interests', 'availability'
            )
        }),
        ('Documents', {
            'fields': (
                'resume', 'photograph', 'completion_certificate'
            )
        }),
        ('Emergency Contact', {
            'fields': (
                'emergency_contact', 'emergency_phone'
            )
        }),
        ('Application Status', {
            'fields': (
                'status', 'approved_by', 'approval_date', 'rejection_reason'
            )
        })
    )

    actions = ['approve_volunteers', 'reject_volunteers', 'export_as_csv']

    def approve_volunteers(self, request, queryset):
        queryset.update(
            status='APPROVED',
            approval_date=now(),
            approved_by=request.user.member_profile
        )
    approve_volunteers.short_description = "Approve selected volunteers"

    def reject_volunteers(self, request, queryset):
        queryset.update(status='REJECTED')
    reject_volunteers.short_description = "Reject selected volunteers"

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}_export_{datetime.now().strftime("%Y_%m_%d")}.csv'
        
        writer = csv.writer(response)
        writer.writerow(field_names)
        
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        
        return response
    export_as_csv.short_description = "Export selected to CSV"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'department',
            'event',
            'initiative',
            'approved_by'
        )