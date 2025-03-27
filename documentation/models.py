# documentation/models.py
from django.db import models
from django.core.validators import MinValueValidator , MaxValueValidator
from django.utils.timezone import now
from users.models import Member
from initiatives.models import Initiative , Event
from monitoring.models import KPIMetric
from program_design.models import InclusionTraining
from decimal import Decimal

from utils.fields import CustomRichTextField


class ProgramLogbook(models.Model):
    ACTIVITY_TYPES = [
        ('WORKSHOP' , 'Workshop Session') ,
        ('OUTREACH' , 'Outreach Campaign') ,
        ('TRAINING' , 'Training Program') ,
        ('MEETING' , 'Stakeholder Meeting') ,
        ('EVENT' , 'Community Event') ,
        ('OTHER' , 'Other Activity')
    ]

    initiative = models.ForeignKey(
        Initiative ,
        on_delete=models.CASCADE ,
        related_name='logbook_entries'
    )
    date = models.DateField(blank=True , default=now)
    activity_type = models.CharField(max_length=20 , choices=ACTIVITY_TYPES,blank=True, null=True)
    activity_description = CustomRichTextField(blank=True, null=True)
    participants_count = models.PositiveIntegerField(default=0,blank=True, null=True)
    milestone_reached = models.TextField(blank=True)
    challenges_faced = models.TextField(blank=True)
    next_steps = CustomRichTextField(blank=True)
    recorded_by = models.ForeignKey(
        Member ,
        on_delete=models.CASCADE ,
        related_name='logbook_entries'
    )
    attachments = models.FileField(
        upload_to='logbook_docs/' ,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']) ,
            models.Index(fields=['activity_type'])
        ]

    def __str__(self):
        return f"{self.initiative.name} - {self.activity_type} ({self.date})"


class DocumentTemplate(models.Model):
    TEMPLATE_TYPES = [
        ('PROGRESS' , 'Progress Report') ,
        ('FEEDBACK' , 'Feedback Form') ,
        ('CSR' , 'CSR Report') ,
        ('IMPACT' , 'Impact Story') ,
        ('LOGBOOK' , 'Logbook Entry')
    ]

    name = models.CharField(max_length=255)
    template_type = models.CharField(max_length=20 , choices=TEMPLATE_TYPES)
    description = CustomRichTextField(blank=True)
    template_content = models.JSONField(
        help_text="JSON structure defining template fields and their properties"
    )
    created_by = models.ForeignKey(
        Member ,
        on_delete=models.CASCADE ,
        related_name='documentation_templates'  # Changed from 'created_templates'
    )
    is_active = models.BooleanField(default=True)
    version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-version']
        unique_together = ['template_type' , 'version']

    def __str__(self):
        return f"{self.name} v{self.version}"


class ImpactStory(models.Model):
    STORY_TYPES = [
        ('SUCCESS' , 'Success Story') ,
        ('TRANSFORMATION' , 'Transformation Journey') ,
        ('TESTIMONIAL' , 'Participant Testimonial') ,
        ('CASE_STUDY' , 'Case Study')
    ]

    SDG_ALIGNMENTS = [
        ('SDG5' , 'SDG 5: Gender Equality') ,
        ('SDG8' , 'SDG 8: Decent Work and Economic Growth')
    ]

    initiative = models.ForeignKey(
        Initiative ,
        on_delete=models.CASCADE ,
        related_name='impact_stories'
    )
    title = models.CharField(max_length=255)
    story_type = models.CharField(max_length=20 , choices=STORY_TYPES)
    participant_name = models.CharField(max_length=255)
    is_anonymous = models.BooleanField(default=False)
    sdg_alignment = models.CharField(max_length=10 , choices=SDG_ALIGNMENTS)
    challenge_description = CustomRichTextField(blank=True)
    solution_provided = CustomRichTextField(blank=True)
    outcome = CustomRichTextField(blank=True)
    testimonial = CustomRichTextField(blank=True)
    metrics_achieved = models.JSONField(
        help_text="JSON object containing relevant metrics and their values"
    )
    media_attachments = models.FileField(
        upload_to='impact_stories/' ,
        blank=True
    )
    approval_status = models.CharField(
        max_length=20 ,
        choices=[
            ('DRAFT' , 'Draft') ,
            ('REVIEW' , 'Under Review') ,
            ('APPROVED' , 'Approved') ,
            ('PUBLISHED' , 'Published')
        ] ,
        default='DRAFT'
    )
    collected_by = models.ForeignKey(
        Member ,
        on_delete=models.CASCADE ,
        related_name='collected_stories'
    )
    approved_by = models.ForeignKey(
        Member ,
        on_delete=models.SET_NULL ,
        null=True ,
        blank=True ,
        related_name='approved_stories'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Impact Stories'

    def __str__(self):
        return f"{self.title} - {self.initiative.name}"


class CSRReport(models.Model):
    REPORT_TYPES = [
        ('MONTHLY' , 'Monthly Update') ,
        ('QUARTERLY' , 'Quarterly Report') ,
        ('ANNUAL' , 'Annual Impact Report')
    ]

    initiative = models.ForeignKey(
        Initiative ,
        on_delete=models.CASCADE ,
        related_name='csr_reports'
    )
    report_type = models.CharField(max_length=20 , choices=REPORT_TYPES)
    period_start = models.DateField()
    period_end = models.DateField()

    # SDG Alignment Metrics
    sdg5_metrics = models.JSONField(
        help_text="JSON object containing SDG 5 related metrics"
    )
    sdg8_metrics = models.JSONField(
        help_text="JSON object containing SDG 8 related metrics"
    )

    # Report Sections
    executive_summary = CustomRichTextField(blank=True)
    program_highlights = CustomRichTextField(blank=True)
    beneficiary_impact = CustomRichTextField(blank=True)
    sdg_alignment_narrative = CustomRichTextField(blank=True)
    challenges_learnings = CustomRichTextField(blank=True)
    future_plans = CustomRichTextField(blank=True)

    # Impact Stories
    featured_stories = models.ManyToManyField(
        ImpactStory ,
        related_name='featured_in_reports'
    )

    # Visual Elements
    dashboard_link = models.URLField(
        blank=True ,
        help_text="Link to Google Data Studio dashboard"
    )

    # Financial Summary
    budget_utilized = models.DecimalField(
        max_digits=10 ,
        decimal_places=2 ,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    cost_per_beneficiary = models.DecimalField(
        max_digits=10 ,
        decimal_places=2 ,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    # Report Status
    status = models.CharField(
        max_length=20 ,
        choices=[
            ('DRAFT' , 'Draft') ,
            ('REVIEW' , 'Under Review') ,
            ('APPROVED' , 'Approved') ,
            ('PUBLISHED' , 'Published')
        ] ,
        default='DRAFT'
    )

    # Workflow
    prepared_by = models.ForeignKey(
        Member ,
        on_delete=models.CASCADE ,
        related_name='prepared_csr_reports'
    )
    reviewed_by = models.ForeignKey(
        Member ,
        on_delete=models.SET_NULL ,
        null=True ,
        blank=True ,
        related_name='reviewed_csr_reports'
    )
    report_file = models.FileField(
        upload_to='csr_reports/' ,
        blank=True
    )
    stakeholder_feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-period_end' , 'report_type']
        unique_together = ['initiative' , 'report_type' , 'period_start' , 'period_end']

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.initiative.name} ({self.period_start} to {self.period_end})"

    def get_sdg_metrics_display(self):
        """Returns formatted SDG metrics for display"""
        sdg5 = self.sdg5_metrics
        sdg8 = self.sdg8_metrics
        return {
            'SDG 5': sdg5 ,
            'SDG 8': sdg8
        }


# documentation/models.py

class ProgressReport(models.Model):
    REPORT_FREQUENCY = [
        ('WEEKLY' , 'Weekly') ,
        ('MONTHLY' , 'Monthly') ,
        ('QUARTERLY' , 'Quarterly') ,
        ('ANNUAL' , 'Annual')
    ]

    initiative = models.ForeignKey(
        'initiatives.Initiative' ,
        on_delete=models.CASCADE ,
        related_name='progress_reports'
    )
    reporting_period = models.CharField(max_length=20 , choices=REPORT_FREQUENCY)
    period_start = models.DateField()
    period_end = models.DateField()
    executive_summary = CustomRichTextField(blank=True)
    achievements = CustomRichTextField(blank=True)
    challenges = CustomRichTextField(blank=True)
    kpi_updates = models.JSONField(
        help_text="JSON object containing KPI updates"
    )
    financial_summary = CustomRichTextField(blank=True)
    next_steps = CustomRichTextField(blank=True)
    prepared_by = models.ForeignKey(
        'users.Member' ,
        on_delete=models.CASCADE ,
        related_name='prepared_progress_reports'
    )
    reviewed_by = models.ForeignKey(
        'users.Member' ,
        on_delete=models.SET_NULL ,
        null=True ,
        blank=True ,
        related_name='reviewed_progress_reports'
    )
    review_comments = models.TextField(blank=True)
    status = models.CharField(
        max_length=20 ,
        choices=[
            ('DRAFT' , 'Draft') ,
            ('SUBMITTED' , 'Submitted') ,
            ('REVIEWED' , 'Reviewed') ,
            ('APPROVED' , 'Approved')
        ] ,
        default='DRAFT'
    )
    report_file = models.FileField(
        upload_to='progress_reports/' ,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-period_end' , 'reporting_period']
        unique_together = ['initiative' , 'period_start' , 'period_end']

    def __str__(self):
        return f"{self.get_reporting_period_display()} Report - {self.initiative.name} ({self.period_start} to {self.period_end})"


class SDGMapping(models.Model):
    SDG_CHOICES = [
        ('SDG5' , 'SDG 5: Gender Equality') ,
        ('SDG8' , 'SDG 8: Decent Work and Economic Growth')
    ]

    initiative = models.ForeignKey(
        'initiatives.Initiative' ,
        on_delete=models.CASCADE ,
        related_name='sdg_mappings'
    )
    sdg = models.CharField(max_length=10 , choices=SDG_CHOICES)
    program_outcome = CustomRichTextField(blank=True)
    impact_area = CustomRichTextField(blank=True)
    metrics = models.JSONField(
        help_text="JSON object containing metrics and targets"
    )
    baseline_value = models.FloatField(null=True , blank=True)
    target_value = models.FloatField()
    current_value = models.FloatField(default=0)
    measurement_method = CustomRichTextField(blank=True)
    data_source = CustomRichTextField(blank=True)
    collection_frequency = models.CharField(
        max_length=20 ,
        choices=[
            ('WEEKLY' , 'Weekly') ,
            ('MONTHLY' , 'Monthly') ,
            ('QUARTERLY' , 'Quarterly') ,
            ('ANNUAL' , 'Annual')
        ]
    )
    responsible_person = models.ForeignKey(
        'users.Member' ,
        on_delete=models.CASCADE ,
        related_name='monitored_sdgs'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sdg' , '-created_at']
        unique_together = ['initiative' , 'sdg']

    def __str__(self):
        return f"{self.get_sdg_display()} - {self.initiative.name}"

    def progress_percentage(self):
        if self.target_value == 0:
            return 0
        return (self.current_value / self.target_value) * 100


class SDGProgress(models.Model):
    sdg_mapping = models.ForeignKey(
        SDGMapping ,
        on_delete=models.CASCADE ,
        related_name='progress_records'
    )
    record_date = models.DateField()
    value = models.FloatField()
    evidence = CustomRichTextField(blank=True)
    supporting_documents = models.FileField(
        upload_to='sdg_evidence/' ,
        blank=True
    )
    recorded_by = models.ForeignKey(
        'users.Member' ,
        on_delete=models.CASCADE ,
        related_name='recorded_sdg_progress'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-record_date']

    def __str__(self):
        return f"{self.sdg_mapping.get_sdg_display()} Progress - {self.record_date}"


class ReportDistribution(models.Model):
    REPORT_TYPES = [
        ('PROGRESS' , 'Progress Report') ,
        ('CSR' , 'CSR Report') ,
        ('IMPACT' , 'Impact Report')
    ]

    DISTRIBUTION_METHODS = [
        ('EMAIL' , 'Email') ,
        ('MEETING' , 'Governance Meeting') ,
        ('PRESENTATION' , 'Stakeholder Presentation')
    ]

    report_type = models.CharField(max_length=20 , choices=REPORT_TYPES)
    # Generic foreign key to handle different report types
    content_type = models.ForeignKey(
        'contenttypes.ContentType' ,
        on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    distribution_date = models.DateField()
    distribution_method = models.CharField(
        max_length=20 ,
        choices=DISTRIBUTION_METHODS
    )
    recipients = models.TextField(
        help_text="List of recipients/stakeholders"
    )
    distributed_by = models.ForeignKey(
        'users.Member' ,
        on_delete=models.CASCADE ,
        related_name='distributed_reports'
    )
    feedback_received = models.TextField(blank=True)
    acknowledgment_status = models.BooleanField(default=False)
    follow_up_required = models.BooleanField(default=False)
    follow_up_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-distribution_date']

    def __str__(self):
        return f"{self.get_report_type_display()} Distribution - {self.distribution_date}"


class DocumentationReview(models.Model):
    REVIEW_TYPES = [
        ('QUARTERLY' , 'Quarterly Logbook Review') ,
        ('ANNUAL' , 'Annual Documentation Audit') ,
        ('ADHOC' , 'Ad-hoc Review')
    ]

    review_type = models.CharField(max_length=20 , choices=REVIEW_TYPES)
    initiative = models.ForeignKey(
        'initiatives.Initiative' ,
        on_delete=models.CASCADE ,
        related_name='documentation_reviews'
    )
    review_date = models.DateField()
    reviewed_by = models.ForeignKey(
        'users.Member' ,
        on_delete=models.CASCADE ,
        related_name='conducted_doc_reviews'
    )
    period_start = models.DateField()
    period_end = models.DateField()
    completeness_check = models.TextField(
        help_text="Assessment of documentation completeness"
    )
    quality_assessment = CustomRichTextField(blank=True)
    identified_gaps = CustomRichTextField(blank=True)
    recommendations = CustomRichTextField(blank=True)
    action_items = CustomRichTextField(blank=True)
    follow_up_date = models.DateField()
    status = models.CharField(
        max_length=20 ,
        choices=[
            ('PENDING' , 'Pending') ,
            ('IN_PROGRESS' , 'In Progress') ,
            ('COMPLETED' , 'Completed')
        ] ,
        default='PENDING'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-review_date']

    def __str__(self):
        return f"{self.get_review_type_display()} - {self.initiative.name} ({self.review_date})"