# monitoring/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.timezone import now
from users.models import Member
from initiatives.models import Initiative, Event
from decimal import Decimal

from utils.fields import CustomRichTextField


class KPIMetric(models.Model):
    METRIC_TYPES = [
        ('BENEFICIARY', 'Number of Beneficiaries'),
        ('SKILL_DEV', 'Skill Development'),
        ('EMPLOYMENT', 'Employment Placement'),
        ('SOCIAL_IMPACT', 'Social Impact'),
        ('FINANCIAL', 'Financial Metric'),
        ('CUSTOM', 'Custom Metric')
    ]

    FREQUENCY_CHOICES = [
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('ANNUALLY', 'Annually')
    ]

    initiative = models.ForeignKey(
        Initiative,
        on_delete=models.CASCADE,
        related_name='kpi_metrics'
    )
    name = models.CharField(max_length=255)
    metric_type = models.CharField(max_length=20, choices=METRIC_TYPES)
    description = CustomRichTextField(blank=True)
    target_value = models.FloatField(validators=[MinValueValidator(0.0)])
    current_value = models.FloatField(default=0.0)
    unit_of_measure = models.CharField(max_length=50)
    monitoring_frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='MONTHLY'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    responsible_person = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='monitored_metrics'
    )
    data_collection_method = models.TextField(
        help_text="How is this metric collected and measured?"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['metric_type', 'name']
        indexes = [
            models.Index(fields=['metric_type']),
            models.Index(fields=['monitoring_frequency'])
        ]

    def __str__(self):
        return f"{self.name} - {self.initiative.name}"

    def completion_percentage(self):
        if self.target_value == 0:
            return 0
        return (self.current_value / self.target_value) * 100

class MetricProgress(models.Model):
    metric = models.ForeignKey(
        KPIMetric,
        on_delete=models.CASCADE,
        related_name='progress_records'
    )
    value = models.FloatField()
    date_recorded = models.DateField()
    recorded_by = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='monitoring_recorded_metrics'  # Changed from 'recorded_metrics'
    )
    notes = models.TextField(blank=True)
    supporting_document = models.FileField(
        upload_to='metric_documents/',
        blank=True
    )

    class Meta:
        ordering = ['-date_recorded']
        indexes = [
            models.Index(fields=['date_recorded'])
        ]

    def __str__(self):
        return f"{self.metric.name} Progress - {self.date_recorded}"

class ParticipantFeedback(models.Model):
    SATISFACTION_CHOICES = [
        (1, 'Very Dissatisfied'),
        (2, 'Dissatisfied'),
        (3, 'Neutral'),
        (4, 'Satisfied'),
        (5, 'Very Satisfied')
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='participant_feedback'
    )
    participant_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    satisfaction_rating = models.IntegerField(
        choices=SATISFACTION_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    most_valuable_aspect = CustomRichTextField(blank=True)
    improvement_suggestions = CustomRichTextField(blank=True)
    would_recommend = models.BooleanField(default=True)
    skills_gained = models.TextField(blank=True)
    confidence_improvement = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    employment_status = models.BooleanField(default=False)
    submission_date = models.DateTimeField(auto_now_add=True)
    is_anonymous = models.BooleanField(default=False)

    class Meta:
        ordering = ['-submission_date']
        indexes = [
            models.Index(fields=['satisfaction_rating']),
            models.Index(fields=['submission_date'])
        ]

    def __str__(self):
        return f"Feedback - {self.event.name} ({self.submission_date})"

class MonitoringCheckIn(models.Model):
    CHECK_IN_TYPES = [
        ('WEEKLY', 'Weekly Check-in'),
        ('MONTHLY', 'Monthly Review'),
        ('QUARTERLY', 'Quarterly Review')
    ]

    initiative = models.ForeignKey(
        Initiative,
        on_delete=models.CASCADE,
        related_name='monitoring_checkins'
    )
    check_in_type = models.CharField(max_length=20, choices=CHECK_IN_TYPES)
    date = models.DateField()
    conducted_by = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='conducted_checkins'
    )
    attendees = models.ManyToManyField(
        Member,
        related_name='attended_checkins'
    )
    progress_summary = CustomRichTextField(blank=True)
    challenges_identified = CustomRichTextField(blank=True)
    action_items = CustomRichTextField(blank=True)
    next_steps = CustomRichTextField(blank=True)
    attachments = models.FileField(
        upload_to='checkin_documents/',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['check_in_type']),
            models.Index(fields=['date'])
        ]

    def __str__(self):
        return f"{self.get_check_in_type_display()} - {self.initiative.name} ({self.date})"

class DataCollectionTemplate(models.Model):
    TEMPLATE_TYPES = [
        ('SURVEY', 'Survey Form'),
        ('CHECKLIST', 'Monitoring Checklist'),
        ('ASSESSMENT', 'Impact Assessment'),
        ('FINANCIAL', 'Financial Report'),
        ('ATTENDANCE', 'Attendance Sheet')
    ]

    name = models.CharField(max_length=255)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    description = CustomRichTextField(blank=True)
    fields = models.JSONField(
        help_text="JSON structure defining form fields and their properties"
    )
    instructions = CustomRichTextField(blank=True)
    created_by = models.ForeignKey(
        Member ,
        on_delete=models.CASCADE ,
        related_name='monitoring_templates'  # Changed from 'created_templates'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['template_type', 'name']
        indexes = [
            models.Index(fields=['template_type']),
            models.Index(fields=['is_active'])
        ]

    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"

class MonitoringReport(models.Model):
    REPORT_TYPES = [
        ('WEEKLY', 'Weekly Progress Report'),
        ('MONTHLY', 'Monthly Progress Report'),
        ('QUARTERLY', 'Quarterly Impact Report'),
        ('ANNUAL', 'Annual Report')
    ]

    initiative = models.ForeignKey(
        Initiative,
        on_delete=models.CASCADE,
        related_name='monitoring_reports'
    )
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    period_start = models.DateField()
    period_end = models.DateField()
    executive_summary = CustomRichTextField(blank=True)
    program_highlights = CustomRichTextField(blank=True)
    kpi_updates = CustomRichTextField(blank=True)
    challenges = CustomRichTextField(blank=True)
    financial_summary = CustomRichTextField(blank=True)
    recommendations = CustomRichTextField(blank=True)
    prepared_by = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='prepared_monitoring_reports'
    )
    reviewed_by = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_monitoring_reports'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('DRAFT', 'Draft'),
            ('REVIEW', 'Under Review'),
            ('APPROVED', 'Approved'),
            ('PUBLISHED', 'Published')
        ],
        default='DRAFT'
    )
    report_file = models.FileField(
        upload_to='monitoring_reports/',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-period_end', 'report_type']
        indexes = [
            models.Index(fields=['report_type']),
            models.Index(fields=['status'])
        ]

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.initiative.name} ({self.period_start} to {self.period_end})"


# monitoring/models.py

class EmploymentTracking(models.Model):
    EMPLOYMENT_STATUS = [
        ('PLACED' , 'Placed in Job') ,
        ('INTERVIEW' , 'In Interview Process') ,
        ('SEARCHING' , 'Actively Searching') ,
        ('NOT_SEEKING' , 'Not Seeking Employment') ,
        ('SELF_EMPLOYED' , 'Self Employed')
    ]

    participant = models.ForeignKey(
        'users.Member' ,
        on_delete=models.CASCADE ,
        related_name='employment_records'
    )
    initiative = models.ForeignKey(
        'initiatives.Initiative' ,
        on_delete=models.CASCADE ,
        related_name='employment_records'
    )
    status = models.CharField(max_length=20 , choices=EMPLOYMENT_STATUS)
    employer_name = models.CharField(max_length=255 , blank=True)
    position = models.CharField(max_length=255 , blank=True)
    salary_range = models.CharField(max_length=100 , blank=True)
    placement_date = models.DateField(null=True , blank=True)
    is_field_related = models.BooleanField(default=True)
    retention_period = models.IntegerField(
        help_text="Employment duration in months" ,
        null=True ,
        blank=True
    )
    skills_utilized = models.TextField(blank=True)
    feedback_from_employer = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.participant.user.get_full_name()} - {self.status}"


class SkillAssessment(models.Model):
    ASSESSMENT_TYPES = [
        ('PRE' , 'Pre-Program Assessment') ,
        ('MID' , 'Mid-Program Assessment') ,
        ('POST' , 'Post-Program Assessment') ,
        ('FOLLOWUP' , 'Follow-up Assessment')
    ]

    participant = models.ForeignKey(
        'users.Member' ,
        on_delete=models.CASCADE ,
        related_name='skill_assessments'
    )
    initiative = models.ForeignKey(
        'initiatives.Initiative' ,
        on_delete=models.CASCADE ,
        related_name='skill_assessments'
    )
    assessment_type = models.CharField(max_length=20 , choices=ASSESSMENT_TYPES)
    assessment_date = models.DateField()
    technical_skills = models.JSONField(
        help_text="JSON object containing skill:rating pairs"
    )
    soft_skills = models.JSONField(
        help_text="JSON object containing skill:rating pairs"
    )
    confidence_score = models.IntegerField(
        validators=[MinValueValidator(1) , MaxValueValidator(5)]
    )
    evaluator = models.ForeignKey(
        'users.Member' ,
        on_delete=models.SET_NULL ,
        null=True ,
        related_name='conducted_assessments'
    )
    recommendations = models.TextField(blank=True)
    improvement_areas = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.participant.user.get_full_name()} - {self.get_assessment_type_display()}"


class WeeklyProgress(models.Model):
    PROGRESS_STATUS = [
        ('ON_TRACK' , 'On Track') ,
        ('AT_RISK' , 'At Risk') ,
        ('DELAYED' , 'Delayed') ,
        ('COMPLETED' , 'Completed')
    ]

    initiative = models.ForeignKey(
        'initiatives.Initiative' ,
        on_delete=models.CASCADE ,
        related_name='weekly_progress'
    )
    week_start_date = models.DateField()
    week_end_date = models.DateField()
    planned_activities = CustomRichTextField(blank=True)
    completed_activities = CustomRichTextField(blank=True)
    status = models.CharField(max_length=20 , choices=PROGRESS_STATUS)
    bottlenecks = models.TextField(blank=True)
    mitigation_steps = models.TextField(blank=True)
    support_needed = models.TextField(blank=True)
    next_week_plan = CustomRichTextField(blank=True)
    recorded_by = models.ForeignKey(
        'users.Member' ,
        on_delete=models.CASCADE ,
        related_name='recorded_weekly_progress'
    )
    team_members = models.ManyToManyField(
        'users.Member' ,
        related_name='weekly_progress_mentions'
    )
    attachments = models.FileField(
        upload_to='weekly_progress/' ,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-week_start_date']
        unique_together = ['initiative' , 'week_start_date']

    def __str__(self):
        return f"{self.initiative.name} - Week of {self.week_start_date}"


class QuarterlyImpactReview(models.Model):
    initiative = models.ForeignKey(
        'initiatives.Initiative' ,
        on_delete=models.CASCADE ,
        related_name='quarterly_reviews'
    )
    year = models.IntegerField()
    quarter = models.IntegerField(
        validators=[MinValueValidator(1) , MaxValueValidator(4)]
    )
    start_date = models.DateField()
    end_date = models.DateField()

    # Impact Metrics
    total_beneficiaries = models.IntegerField(default=0)
    skill_completion_rate = models.FloatField(
        validators=[MinValueValidator(0.0) , MaxValueValidator(100.0)]
    )
    employment_rate = models.FloatField(
        validators=[MinValueValidator(0.0) , MaxValueValidator(100.0)]
    )
    avg_confidence_score = models.FloatField(
        validators=[MinValueValidator(1.0) , MaxValueValidator(5.0)]
    )

    # Financial Metrics
    budget_utilized = models.DecimalField(
        max_digits=10 ,
        decimal_places=2 ,
        default=Decimal('0.00')
    )
    cost_per_beneficiary = models.DecimalField(
        max_digits=10 ,
        decimal_places=2 ,
        default=Decimal('0.00')
    )

    key_achievements = CustomRichTextField(blank=True)
    challenges_faced = CustomRichTextField(blank=True)
    lessons_learned = CustomRichTextField(blank=True)
    recommendations = CustomRichTextField(blank=True)
    next_quarter_focus = CustomRichTextField(blank=True)

    prepared_by = models.ForeignKey(
        'users.Member' ,
        on_delete=models.CASCADE ,
        related_name='prepared_quarterly_reviews'
    )
    reviewed_by = models.ForeignKey(
        'users.Member' ,
        on_delete=models.SET_NULL ,
        null=True ,
        related_name='reviewed_quarterly_reviews'
    )
    presentation_file = models.FileField(
        upload_to='quarterly_reviews/' ,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year' , '-quarter']
        unique_together = ['initiative' , 'year' , 'quarter']

    def __str__(self):
        return f"{self.initiative.name} - Q{self.quarter} {self.year}"


class FinancialTracking(models.Model):
    EXPENSE_CATEGORIES = [
        ('STAFF' , 'Staff Salaries') ,
        ('MATERIALS' , 'Materials & Supplies') ,
        ('VENUE' , 'Venue Rentals') ,
        ('TRANSPORT' , 'Transportation') ,
        ('REFRESHMENTS' , 'Refreshments') ,
        ('MARKETING' , 'Marketing & Outreach') ,
        ('MISC' , 'Miscellaneous')
    ]

    initiative = models.ForeignKey(
        'initiatives.Initiative' ,
        on_delete=models.CASCADE ,
        related_name='financial_records'
    )
    month = models.DateField()
    category = models.CharField(max_length=20 , choices=EXPENSE_CATEGORIES)
    description = CustomRichTextField(blank=True)
    budgeted_amount = models.DecimalField(
        max_digits=10 ,
        decimal_places=2 ,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    actual_amount = models.DecimalField(
        max_digits=10 ,
        decimal_places=2 ,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    variance_notes = models.TextField(blank=True)
    bills_attachment = models.FileField(
        upload_to='financial_records/' ,
        blank=True
    )
    recorded_by = models.ForeignKey(
        'users.Member' ,
        on_delete=models.CASCADE ,
        related_name='recorded_finances'
    )
    approved_by = models.ForeignKey(
        'users.Member' ,
        on_delete=models.SET_NULL ,
        null=True ,
        related_name='approved_finances'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-month' , 'category']

    def __str__(self):
        return f"{self.initiative.name} - {self.get_category_display()} - {self.month}"

    def variance_amount(self):
        return self.actual_amount - self.budgeted_amount

    def variance_percentage(self):
        if self.budgeted_amount == 0:
            return 0
        return (self.variance_amount() / self.budgeted_amount) * 100