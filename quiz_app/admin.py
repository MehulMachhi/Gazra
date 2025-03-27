from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.db.models import Count, Avg, Sum, Min, Max, F, ExpressionWrapper, fields
from django.utils.html import format_html
from django.urls import reverse, path
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
import csv
import json
from datetime import timedelta
from .models import (
    Survey, QuestionType, Question, QuestionChoice, 
    SurveyResponse, QuestionResponse
)


class QuestionChoiceInline(admin.TabularInline):
    model = QuestionChoice
    extra = 3
    fields = ('text', 'order')


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('text', 'question_type', 'is_required', 'order', 'allow_multiple')
    show_change_link = True


class QuestionResponseInline(admin.TabularInline):
    model = QuestionResponse
    extra = 0
    fields = ('question', 'text_response', 'number_response', 'date_response', 'file_response', 'get_selected_choices')
    readonly_fields = ('question', 'text_response', 'number_response', 'date_response', 'file_response', 'get_selected_choices')
    can_delete = False
    max_num = 0
    
    def get_selected_choices(self, obj):
        return ", ".join([choice.text for choice in obj.selected_choices.all()])
    get_selected_choices.short_description = "Selected Choices"


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at', 'is_active', 'response_count', 'question_count', 'completion_rate_display')
    list_filter = ('is_active', 'created_at', 'created_by')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [QuestionInline]
    date_hierarchy = 'created_at'
    actions = ['export_responses_csv', 'duplicate_survey', 'deactivate_surveys', 'activate_surveys']
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'slug', 'is_active')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date'),
            'classes': ('collapse',),
        }),
        ('Ownership', {
            'fields': ('created_by',),
            'classes': ('collapse',),
        }),
    )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:survey_id>/analytics/',
                self.admin_site.admin_view(self.survey_analytics_view),
                name='survey_analytics',
            ),
        ]
        return custom_urls + urls
    
    def completion_rate_display(self, obj):
        return f"{obj.completion_rate:.1f}%"
    completion_rate_display.short_description = "Completion Rate"
    
    # def response_count(self, obj):
    #     count = obj.response_count
    #     url = reverse('admin:survey_app_surveyresponse_changelist') + f'?survey_id_exact={obj.id}'
    #     return format_html('<a href="{}">{}</a>', url, count)
    # response_count.short_description = "Responses"
    
    # def question_count(self, obj):
    #     count = obj.question_count
    #     url = reverse('admin:survey_app_question_changelist') + f'?survey_id_exact={obj.id}'
    #     return format_html('<a href="{}">{}</a>', url, count)
    # question_count.short_description = "Questions"
    
    def export_responses_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="survey_responses.csv"'
        
        writer = csv.writer(response)
        
        for survey in queryset:
            # Add survey title as header
            writer.writerow([f"Survey: {survey.title}"])
            
            # Get all questions for this survey
            questions = survey.questions.all().order_by('order')
            
            # Write question headers
            header_row = ['Respondent ID', 'Started At', 'Completed At', 'Completion Status']
            for question in questions:
                header_row.append(question.text)
            writer.writerow(header_row)
            
            # Write response data
            responses = SurveyResponse.objects.filter(survey=survey)
            for resp in responses:
                row = [
                    resp.submission_id,
                    resp.started_at,
                    resp.completed_at if resp.completed_at else "Incomplete",
                    "Complete" if resp.is_complete else "Incomplete"
                ]
                
                # Add response data for each question
                for question in questions:
                    try:
                        q_response = QuestionResponse.objects.get(survey_response=resp, question=question)
                        
                        if q_response.response_type == 'text':
                            row.append(q_response.text_response)
                        elif q_response.response_type == 'number':
                            row.append(q_response.number_response)
                        elif q_response.response_type == 'date':
                            row.append(q_response.date_response)
                        elif q_response.response_type == 'choice':
                            choices = q_response.selected_choices.all()
                            row.append(", ".join([c.text for c in choices]))
                        elif q_response.response_type == 'file':
                            row.append(q_response.file_response.url if q_response.file_response else "")
                        else:
                            row.append("")
                    except QuestionResponse.DoesNotExist:
                        row.append("")
                
                writer.writerow(row)
            
            # Add a blank row between surveys
            writer.writerow([])
        
        return response
    export_responses_csv.short_description = "Export selected surveys to CSV"
    
    def duplicate_survey(self, request, queryset):
        for survey in queryset:
            # Create a new survey
            new_survey = Survey.objects.create(
                title=f"Copy of {survey.title}",
                description=survey.description,
                slug=f"{survey.slug}-copy-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                is_active=False,
                created_by=request.user,
                start_date=timezone.now(),
                end_date=survey.end_date
            )
            
            # Duplicate questions
            for question in survey.questions.all():
                new_question = Question.objects.create(
                    survey=new_survey,
                    question_type=question.question_type,
                    text=question.text,
                    description=question.description,
                    is_required=question.is_required,
                    order=question.order,
                    min_value=question.min_value,
                    max_value=question.max_value,
                    allow_multiple=question.allow_multiple
                )
                
                # Duplicate choices
                for choice in question.choices.all():
                    QuestionChoice.objects.create(
                        question=new_question,
                        text=choice.text,
                        order=choice.order
                    )
            
            self.message_user(request, f"Survey '{survey.title}' was duplicated successfully.")
    duplicate_survey.short_description = "Duplicate selected surveys"
    
    def deactivate_surveys(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} surveys have been deactivated.")
    deactivate_surveys.short_description = "Deactivate selected surveys"
    
    def activate_surveys(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} surveys have been activated.")
    activate_surveys.short_description = "Activate selected surveys"
    
    def survey_analytics_view(self, request, survey_id):
        """Custom view to display survey analytics"""
        survey = Survey.objects.get(pk=survey_id)
        
        # Basic survey stats
        total_responses = SurveyResponse.objects.filter(survey=survey).count()
        complete_responses = SurveyResponse.objects.filter(survey=survey, is_complete=True).count()
        incomplete_responses = total_responses - complete_responses
        
        # Response over time data
        last_30_days = timezone.now() - timedelta(days=30)
        daily_responses = (
            SurveyResponse.objects
            .filter(survey=survey, started_at__gte=last_30_days)
            .extra({'date': "date(started_at)"})
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )
        
        # Calculate average completion time
        completed_responses = SurveyResponse.objects.filter(
            survey=survey, 
            is_complete=True, 
            completed_at__isnull=False
        )
        
        avg_completion_seconds = 0
        if completed_responses.exists():
            total_seconds = 0
            count = 0
            for response in completed_responses:
                if response.completion_time:
                    total_seconds += response.completion_time.total_seconds()
                    count += 1
            
            if count > 0:
                avg_completion_seconds = total_seconds / count
        
        # Process question responses
        questions = survey.questions.all().order_by('order')
        question_stats = []
        
        for question in questions:
            stat = {
                'id': question.id,
                'text': question.text,
                'type': question.question_type.name,
                'response_count': question.response_count,
            }
            
            # Additional stats based on question type
            if question.question_type.type_code == QuestionType.SINGLE_CHOICE or \
               question.question_type.type_code == QuestionType.MULTIPLE_CHOICE:
                choices = question.choices.all()
                choice_stats = []
                
                for choice in choices:
                    choice_stats.append({
                        'text': choice.text,
                        'count': choice.response_count,
                        'percentage': choice.response_percentage,
                    })
                
                stat['choices'] = choice_stats
            
            elif question.question_type.type_code == QuestionType.RATING or \
                 question.question_type.type_code == QuestionType.NUMBER:
                # Get average, min, max for number/rating questions
                number_responses = QuestionResponse.objects.filter(
                    question=question,
                    number_response__isnull=False
                )
                
                if number_responses.exists():
                    stat['average'] = number_responses.aggregate(Avg('number_response'))['number_response__avg']
                    stat['min'] = number_responses.aggregate(Min('number_response'))['number_response__min']
                    stat['max'] = number_responses.aggregate(Max('number_response'))['number_response__max']
            
            question_stats.append(stat)
        
        # Prepare chart data for JavaScript
        chart_data = {
            'daily_responses': list(daily_responses),
            'completion_rate': {
                'complete': complete_responses,
                'incomplete': incomplete_responses
            },
            'question_stats': question_stats
        }
        
        context = {
            'survey': survey,
            'total_responses': total_responses,
            'complete_responses': complete_responses,
            'completion_rate': survey.completion_rate,
            'avg_completion_time': timedelta(seconds=avg_completion_seconds),
            'question_stats': question_stats,
            'chart_data': json.dumps(chart_data),
            'opts': self.model._meta,
        }
        
        return render(request, 'admin/survey_analytics.html', context)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'survey', 'question_type', 'is_required', 'order', 'response_count', 'choice_count')
    list_filter = ('survey', 'question_type', 'is_required')
    search_fields = ('text', 'description')
    inlines = [QuestionChoiceInline]
    fieldsets = (
        (None, {
            'fields': ('survey', 'text', 'description', 'question_type', 'is_required', 'order')
        }),
        ('Advanced Options', {
            'fields': ('allow_multiple', 'min_value', 'max_value'),
            'classes': ('collapse',),
        }),
    )


@admin.register(QuestionType)
class QuestionTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'type_code', 'description')
    search_fields = ('name', 'description')


@admin.register(QuestionChoice)
class QuestionChoiceAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'order', 'response_count', 'response_percentage')
    list_filter = ('question__survey', 'question')
    search_fields = ('text', 'question__text')


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ('submission_id', 'survey', 'respondent', 'started_at', 'completed_at', 'is_complete', 'completion_time_display')
    list_filter = ('survey', 'is_complete', 'started_at')
    search_fields = ('submission_id', 'respondent__username', 'respondent_ip')
    readonly_fields = ('submission_id', 'started_at', 'completion_time_display')
    inlines = [QuestionResponseInline]
    date_hierarchy = 'started_at'
    actions = ['export_selected_responses']
    
    def completion_time_display(self, obj):
        if obj.completion_time:
            return str(obj.completion_time).split('.')[0]  # Remove microseconds
        return "Not completed"
    completion_time_display.short_description = "Completion Time"
    
    def export_selected_responses(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="selected_responses.csv"'
        
        writer = csv.writer(response)
        
        # Group responses by survey
        survey_responses = {}
        for resp in queryset:
            if resp.survey_id not in survey_responses:
                survey_responses[resp.survey_id] = {
                    'survey': resp.survey,
                    'responses': []
                }
            survey_responses[resp.survey_id]['responses'].append(resp)
        
        # Process each survey separately
        for survey_id, data in survey_responses.items():
            survey = data['survey']
            responses = data['responses']
            
            # Add survey title as header
            writer.writerow([f"Survey: {survey.title}"])
            
            # Get all questions for this survey
            questions = survey.questions.all().order_by('order')
            
            # Write question headers
            header_row = ['Respondent ID', 'Started At', 'Completed At', 'Completion Status']
            for question in questions:
                header_row.append(question.text)
            writer.writerow(header_row)
            
            # Write response data
            for resp in responses:
                row = [
                    resp.submission_id,
                    resp.started_at,
                    resp.completed_at if resp.completed_at else "Incomplete",
                    "Complete" if resp.is_complete else "Incomplete"
                ]
                
                # Add response data for each question
                for question in questions:
                    try:
                        q_response = QuestionResponse.objects.get(survey_response=resp, question=question)
                        
                        if q_response.response_type == 'text':
                            row.append(q_response.text_response)
                        elif q_response.response_type == 'number':
                            row.append(q_response.number_response)
                        elif q_response.response_type == 'date':
                            row.append(q_response.date_response)
                        elif q_response.response_type == 'choice':
                            choices = q_response.selected_choices.all()
                            row.append(", ".join([c.text for c in choices]))
                        elif q_response.response_type == 'file':
                            row.append(q_response.file_response.url if q_response.file_response else "")
                        else:
                            row.append("")
                    except QuestionResponse.DoesNotExist:
                        row.append("")
                
                writer.writerow(row)
            
            # Add a blank row between surveys
            writer.writerow([])
        
        return response
    export_selected_responses.short_description = "Export selected responses to CSV"


@admin.register(QuestionResponse)
class QuestionResponseAdmin(admin.ModelAdmin):
    list_display = ('question', 'survey_response', 'response_summary', 'created_at')
    list_filter = ('question__survey', 'question', 'created_at')
    search_fields = ('text_response', 'question_text', 'survey_response_submission_id')
    readonly_fields = ('question', 'survey_response', 'created_at')
    
    def response_summary(self, obj):
        if obj.response_type == 'text':
            return obj.text_response[:50] + "..." if len(obj.text_response) > 50 else obj.text_response
        elif obj.response_type == 'number':
            return obj.number_response
        elif obj.response_type == 'date':
            return obj.date_response
        elif obj.response_type == 'choice':
            choices = obj.selected_choices.all()
            return ", ".join([c.text for c in choices])
        elif obj.response_type == 'file':
            return "File uploaded" if obj.file_response else "No file"
        return "No response"
    response_summary.short_description = "Response"