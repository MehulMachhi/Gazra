# program_design/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from initiatives.models import Initiative
from users.models import Member
import datetime

from utils.fields import CustomRichTextField


class DiversityMetric(models.Model):
    initiative = models.ForeignKey(
        Initiative,
        on_delete=models.CASCADE,
        related_name='diversity_metrics'
    )
    date_recorded = models.DateField(auto_now_add=True)
    women_participants_count = models.PositiveIntegerField(default=0)
    lgbtqia_participants_count = models.PositiveIntegerField(default=0)
    marginalized_participants_count = models.PositiveIntegerField(default=0)
    total_participants = models.PositiveIntegerField(default=0)
    recorded_by = models.ForeignKey(
        Member ,
        on_delete=models.SET_NULL ,
        null=True ,
        related_name='diversity_recorded_metrics'  # Changed from 'recorded_metrics'
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Diversity Metrics - {self.initiative.name} ({self.date_recorded})"

    def women_percentage(self):
        return (self.women_participants_count / self.total_participants * 100) if self.total_participants > 0 else 0

    def lgbtqia_percentage(self):
        return (self.lgbtqia_participants_count / self.total_participants * 100) if self.total_participants > 0 else 0

    def marginalized_percentage(self):
        return (self.marginalized_participants_count / self.total_participants * 100) if self.total_participants > 0 else 0

class CoCreationWorkshop(models.Model):
    STATUS_CHOICES = [
        ('PLANNED', 'Planned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled')
    ]

    initiative = models.ForeignKey(
        Initiative,
        on_delete=models.CASCADE,
        related_name='cocreation_workshops'
    )
    title = models.CharField(max_length=255)
    date = models.DateField()
    location = models.CharField(max_length=255)
    facilitator = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,
        null=True,
        related_name='facilitated_workshops'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PLANNED'
    )
    total_participants = models.PositiveIntegerField(default=0)
    women_count = models.PositiveIntegerField(default=0)
    lgbtqia_count = models.PositiveIntegerField(default=0)
    marginalized_count = models.PositiveIntegerField(default=0)
    agenda = CustomRichTextField(blank=True)
    outcomes = models.TextField(blank=True)
    next_steps = models.TextField(blank=True)
    materials_used = models.TextField(blank=True)
    attachments = models.FileField(
        upload_to='workshop_materials/',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['date'])
        ]

    def __str__(self):
        return f"{self.title} - {self.initiative.name}"

class InclusionTraining(models.Model):
    TRAINING_TYPES = [
        ('STEREOTYPE_BIAS', 'Understanding Stereotypes and Bias'),
        ('INCLUSIVE_COMM', 'Inclusive Communication'),
        ('CULTURAL_SENSITIVITY', 'Cultural Sensitivity'),
        ('CASE_STUDIES', 'Case Studies and Role Play')
    ]

    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled')
    ]

    title = models.CharField(max_length=255)
    training_type = models.CharField(max_length=50, choices=TRAINING_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    facilitator = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,
        null=True,
        related_name='facilitated_trainings'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='SCHEDULED'
    )
    participants = models.ManyToManyField(
        Member,
        related_name='attended_trainings'
    )
    description = CustomRichTextField(blank=True)
    objectives = CustomRichTextField(blank=True)
    materials = models.FileField(
        upload_to='training_materials/',
        blank=True
    )
    feedback_summary = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['training_type']),
            models.Index(fields=['status'])
        ]

    def __str__(self):
        return f"{self.title} ({self.get_training_type_display()})"

class CulturalSensitivityAudit(models.Model):
    AUDIT_TYPES = [
        ('PROGRAM', 'Program Audit'),
        ('COMMUNICATION', 'Communication Audit'),
        ('MATERIAL', 'Material Audit'),
        ('FEEDBACK', 'Feedback Analysis')
    ]

    initiative = models.ForeignKey(
        Initiative,
        on_delete=models.CASCADE,
        related_name='sensitivity_audits'
    )
    audit_type = models.CharField(max_length=20, choices=AUDIT_TYPES)
    audit_date = models.DateField()
    auditor = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,
        null=True,
        related_name='conducted_audits'
    )
    findings = CustomRichTextField(blank=True)
    recommendations = CustomRichTextField(blank=True)
    action_items = CustomRichTextField(blank=True)
    follow_up_date = models.DateField()
    completion_status = models.BooleanField(default=False)
    attachments = models.FileField(
        upload_to='audit_documents/',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-audit_date']
        indexes = [
            models.Index(fields=['audit_type']),
            models.Index(fields=['completion_status'])
        ]

    def __str__(self):
        return f"{self.get_audit_type_display()} - {self.initiative.name}"

class ProgramFeedback(models.Model):
    FEEDBACK_CATEGORIES = [
        ('CONTENT', 'Program Content'),
        ('DELIVERY', 'Program Delivery'),
        ('INCLUSION', 'Inclusivity'),
        ('CULTURAL', 'Cultural Sensitivity'),
        ('GENERAL', 'General Feedback')
    ]

    initiative = models.ForeignKey(
        Initiative,
        on_delete=models.CASCADE,
        related_name='program_feedback'
    )
    category = models.CharField(max_length=20, choices=FEEDBACK_CATEGORIES)
    feedback_text = CustomRichTextField(blank=True)
    submitted_by = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    is_anonymous = models.BooleanField(default=False)
    expectations_met = models.BooleanField(default=True)
    culturally_sensitive = models.BooleanField(default=True)
    improvement_suggestions = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reviewed_feedback'
    )
    action_taken = models.TextField(blank=True)

    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['submitted_at'])
        ]

    def __str__(self):
        return f"{self.get_category_display()} Feedback - {self.initiative.name}"