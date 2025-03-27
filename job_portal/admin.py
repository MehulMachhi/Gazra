from django.contrib import admin

# Register your models here.
# admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import (
    Industry, Skill, Company, CompanyReview, JobSeeker, JobSeekerSkill,
    Experience, Education, Job, JobApplication, JobAlert, SavedJob,
    Interview, Assessment, Notification, Message, JobSeekerPreference,
    CompanyFollower
)
class JobSeekerSkillInline(admin.TabularInline):
    model = JobSeekerSkill
    extra = 1
    autocomplete_fields = ['skill']

class ExperienceInline(admin.StackedInline):
    model = Experience
    extra = 0

class EducationInline(admin.StackedInline):
    model = Education
    extra = 0

@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('name',)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset = queryset.filter(name__icontains=search_term)
        return queryset, use_distinct

class CompanyReviewInline(admin.TabularInline):
    model = CompanyReview
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = ('company_name', 'user', 'industry', 'is_verified', 'is_featured', 'created_at')
    list_filter = ('is_verified', 'is_featured', 'industry', 'company_size')
    search_fields = ('company_name', 'user__username', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CompanyReviewInline]
    actions = ['verify_companies', 'feature_companies']

    def verify_companies(self, request, queryset):
        queryset.update(is_verified=True)
    verify_companies.short_description = "Mark selected companies as verified"

    def feature_companies(self, request, queryset):
        queryset.update(is_featured=True)
    feature_companies.short_description = "Mark selected companies as featured"

class ExperienceInline(admin.StackedInline):
    model = Experience
    extra = 0

class EducationInline(admin.StackedInline):
    model = Education
    extra = 0




@admin.register(JobSeeker)
class JobSeekerAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = ('user', 'experience_years', 'is_available', 'profile_visibility', 'created_at')
    list_filter = ('is_available', 'profile_visibility', 'preferred_industries')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [JobSeekerSkillInline, ExperienceInline, EducationInline]
    filter_horizontal = ('preferred_industries',)  # Only for direct M2M relationships

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            'skills', 'preferred_industries', 'experiences', 'educations'
        )

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = ('title', 'company', 'location', 'job_type', 'status', 'is_featured', 'applications_count', 'posted_date')
    list_filter = ('status', 'job_type', 'experience_level', 'is_featured', 'is_remote')
    search_fields = ('title', 'company__company_name', 'description')
    readonly_fields = ('applications_count', 'views_count', 'created_at', 'updated_at')
    filter_horizontal = ('skills_required', 'skills_preferred')
    actions = ['mark_as_active', 'mark_as_featured', 'mark_as_closed']

    def mark_as_active(self, request, queryset):
        queryset.update(status='AC')
    mark_as_active.short_description = "Mark selected jobs as active"

    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
    mark_as_featured.short_description = "Mark selected jobs as featured"

    def mark_as_closed(self, request, queryset):
        queryset.update(status='CL')
    mark_as_closed.short_description = "Mark selected jobs as closed"

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = ('applicant', 'job', 'status', 'applied_date', 'is_viewed')
    list_filter = ('status', 'is_viewed', 'applied_date')
    search_fields = ('applicant__user__username', 'job__title', 'job__company__company_name')
    readonly_fields = ('applied_date', 'updated_at')
    actions = ['mark_as_viewed', 'move_to_reviewing', 'mark_as_shortlisted']

    def mark_as_viewed(self, request, queryset):
        queryset.update(is_viewed=True, viewed_date=timezone.now())
    mark_as_viewed.short_description = "Mark selected applications as viewed"

    def move_to_reviewing(self, request, queryset):
        queryset.update(status='RV')
    move_to_reviewing.short_description = "Move selected applications to reviewing"

    def mark_as_shortlisted(self, request, queryset):
        queryset.update(status='SC')
    mark_as_shortlisted.short_description = "Mark selected applications as shortlisted"

@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = ('application', 'interview_type', 'scheduled_date', 'status', 'interviewer')
    list_filter = ('interview_type', 'status', 'scheduled_date')
    search_fields = ('application__applicant__user__username', 'application__job__title')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = ('title', 'application', 'assessment_type', 'deadline', 'is_completed', 'score')
    list_filter = ('assessment_type', 'is_completed', 'deadline')
    search_fields = ('title', 'application__applicant__user__username', 'application__job__title')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(JobAlert)
class JobAlertAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = ('user', 'keywords', 'frequency', 'is_active', 'last_sent')
    list_filter = ('frequency', 'is_active', 'created_at')
    search_fields = ('user__username', 'keywords')
    readonly_fields = ('created_at', 'last_sent')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    readonly_fields = ('created_at',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False
    list_display = ('sender', 'receiver', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'receiver__username', 'subject', 'content')
    readonly_fields = ('created_at', 'read_at')

# Register remaining models
@admin.register(JobSeekerSkill)
class JobSeekerSkillAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False

@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False

@admin.register(CompanyReview)
class CompanyReviewAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False

@admin.register(CompanyFollower)
class CompanyFollowerAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False

@admin.register(JobSeekerPreference)
class JobSeekerPreferenceAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return False