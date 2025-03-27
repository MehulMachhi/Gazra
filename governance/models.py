# governance/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.timezone import now
from users.models import Member, Department
from initiatives.models import Initiative
from decimal import Decimal

from utils.fields import CustomRichTextField


class TeamRole(models.Model):
    ROLE_TYPES = [
        ('PROGRAM_MANAGER', 'Program Manager'),
        ('FIELD_COORDINATOR', 'Field Coordinator'),
        ('ME_OFFICER', 'M&E Officer'),
        ('FINANCE_OFFICER', 'Finance Officer'),
        ('COMMUNICATIONS_LEAD', 'Communications Lead')
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='team_roles')
    role_type = models.CharField(max_length=50, choices=ROLE_TYPES)
    initiatives = models.ManyToManyField(Initiative, related_name='team_members')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    responsibilities = CustomRichTextField(blank=True)
    tools_used = models.TextField(help_text="List of tools used (e.g., Asana, Trello)")
    is_active = models.BooleanField(default=True)
    reporting_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='team_members'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['member', 'role_type', 'is_active']

    def __str__(self):
        return f"{self.member.user.get_full_name()} - {self.get_role_type_display()}"

class ResourceAllocation(models.Model):
    RESOURCE_TYPES = [
        ('STAFF', 'Staff Salaries'),
        ('MATERIALS', 'Materials'),
        ('VENUE', 'Venue Rental'),
        ('TRANSPORT', 'Transportation'),
        ('TECHNOLOGY', 'Technology'),
        ('MARKETING', 'Marketing'),
        ('OTHER', 'Other')
    ]

    STATUS_CHOICES = [
        ('REQUESTED', 'Requested'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed')
    ]

    initiative = models.ForeignKey(
        Initiative,
        on_delete=models.CASCADE,
        related_name='resource_allocations'
    )
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    description = CustomRichTextField(blank=True)
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    actual_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    quantity = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REQUESTED')
    requested_by = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='resource_requests'
    )
    approved_by = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_resources'
    )
    requested_date = models.DateField(auto_now_add=True)
    required_by_date = models.DateField()
    procurement_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_resource_type_display()} - {self.initiative.name}"

class ProjectTimeline(models.Model):
    PRIORITY_LEVELS = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent')
    ]

    STATUS_CHOICES = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('DELAYED', 'Delayed'),
        ('ON_HOLD', 'On Hold')
    ]

    initiative = models.ForeignKey(
        Initiative,
        on_delete=models.CASCADE,
        related_name='project_timelines'
    )
    task_name = models.CharField(max_length=255)
    description = CustomRichTextField(blank=True)
    assigned_to = models.ForeignKey(
        Member ,
        on_delete=models.CASCADE ,
        related_name='governance_assigned_tasks'  # Changed from 'assigned_tasks'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    progress = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    dependencies = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='dependent_tasks'
    )
    tool_link = models.URLField(
        help_text="Link to task in project management tool",
        blank=True
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.task_name} - {self.initiative.name}"

class RiskAssessment(models.Model):
    RISK_TYPES = [
        ('POLITICAL', 'Political Risk'),
        ('FUNDING', 'Funding Risk'),
        ('OPERATIONAL', 'Operational Risk'),
        ('REPUTATIONAL', 'Reputational Risk'),
        ('COMPLIANCE', 'Compliance Risk'),
        ('SECURITY', 'Security Risk')
    ]

    LIKELIHOOD_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High')
    ]

    IMPACT_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High')
    ]

    STATUS_CHOICES = [
        ('IDENTIFIED', 'Identified'),
        ('MONITORED', 'Being Monitored'),
        ('MITIGATED', 'Mitigated'),
        ('OCCURRED', 'Risk Occurred'),
        ('CLOSED', 'Closed')
    ]

    initiative = models.ForeignKey(
        Initiative,
        on_delete=models.CASCADE,
        related_name='risk_assessments'
    )
    risk_type = models.CharField(max_length=20, choices=RISK_TYPES)
    description = CustomRichTextField(blank=True)
    likelihood = models.CharField(max_length=20, choices=LIKELIHOOD_CHOICES)
    impact = models.CharField(max_length=20, choices=IMPACT_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IDENTIFIED')
    identified_by = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='identified_risks'
    )
    assigned_to = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='assigned_risks'
    )
    identification_date = models.DateField(auto_now_add=True)
    last_review_date = models.DateField(auto_now=True)
    next_review_date = models.DateField()
    mitigation_plan = CustomRichTextField(blank=True)
    contingency_plan = CustomRichTextField(blank=True)
    fallback_strategy = CustomRichTextField(blank=True)
    actual_impact = models.TextField(blank=True)
    resolution_date = models.DateField(null=True, blank=True)
    lessons_learned = models.TextField(blank=True)
    attachments = models.FileField(
        upload_to='risk_documents/',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_risk_type_display()} - {self.initiative.name}"

    def risk_score(self):
        likelihood_score = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3}
        impact_score = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3}
        return likelihood_score[self.likelihood] * impact_score[self.impact]

class GovernanceBody(models.Model):
    COMMITTEE_TYPES = [
        ('OVERSIGHT', 'Oversight Committee'),
        ('FINANCE', 'Finance Committee'),
        ('AUDIT', 'Audit Committee'),
        ('PROGRAM', 'Program Committee')
    ]

    name = models.CharField(max_length=255)
    committee_type = models.CharField(max_length=20, choices=COMMITTEE_TYPES)
    description = CustomRichTextField(blank=True)
    chairperson = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='chaired_committees'
    )
    secretary = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='secretary_committees'
    )
    members = models.ManyToManyField(Member, related_name='committee_memberships')
    formation_date = models.DateField()
    tenure_end_date = models.DateField()
    meeting_frequency = models.CharField(
        max_length=50,
        choices=[
            ('WEEKLY', 'Weekly'),
            ('BIWEEKLY', 'Bi-weekly'),
            ('MONTHLY', 'Monthly'),
            ('QUARTERLY', 'Quarterly')
        ]
    )
    quorum_requirement = CustomRichTextField(blank=True)
    terms_of_reference = CustomRichTextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_committee_type_display()})"

class GovernanceMeeting(models.Model):
    governance_body = models.ForeignKey(
        GovernanceBody,
        on_delete=models.CASCADE,
        related_name='meetings'
    )
    meeting_date = models.DateTimeField()
    agenda = CustomRichTextField(blank=True)
    attendees = models.ManyToManyField(Member, related_name='attended_meetings')
    minutes = CustomRichTextField(blank=True)
    decisions_made = CustomRichTextField(blank=True)
    action_items = CustomRichTextField(blank=True)
    next_meeting_date = models.DateTimeField()
    attachments = models.FileField(
        upload_to='meeting_documents/',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.governance_body.name} Meeting - {self.meeting_date}"

class CSRProposal(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('REVIEW', 'Under Review'),
        ('SUBMITTED', 'Submitted'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('AWARDED', 'Awarded')
    ]

    title = models.CharField(max_length=255)
    initiative = models.ForeignKey(
        Initiative,
        on_delete=models.CASCADE,
        related_name='csr_proposals'
    )
    company_name = models.CharField(max_length=255)
    submission_deadline = models.DateField()
    requested_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    approved_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    prepared_by = models.ForeignKey(
        Member ,
        on_delete=models.CASCADE ,
        related_name='governance_prepared_proposals'  # Changed from 'prepared_proposals'
    )
    reviewed_by = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_proposals'
    )
    executive_summary = CustomRichTextField(blank=True)
    alignment_with_sdgs = CustomRichTextField(blank=True)
    budget_breakdown = CustomRichTextField(blank=True)
    impact_metrics = CustomRichTextField(blank=True)
    partnership_details = CustomRichTextField(blank=True)
    submission_date = models.DateField(null=True, blank=True)
    feedback_received = models.TextField(blank=True)
    proposal_document = models.FileField(
        upload_to='csr_proposals/',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.company_name}"

class GovernanceReport(models.Model):
    REPORT_TYPES = [
        ('MONTHLY', 'Monthly Report'),
        ('QUARTERLY', 'Quarterly Report'),
        ('ANNUAL', 'Annual Report')
    ]

    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    period_start = models.DateField()
    period_end = models.DateField()
    prepared_by = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='prepared_reports'
    )
    executive_summary = CustomRichTextField(blank=True)
    progress_overview = CustomRichTextField(blank=True)
    financial_overview = CustomRichTextField(blank=True)
    challenges_risks = CustomRichTextField(blank=True)
    recommendations = CustomRichTextField(blank=True)
    attachments = models.FileField(
        upload_to='governance_reports/',
        blank=True
    )
    submitted_date = models.DateField()
    approved_by = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_reports'
    )
    approval_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.period_start} to {self.period_end}"