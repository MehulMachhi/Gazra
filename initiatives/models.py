# initiatives/models.py
from django.db import models
from django.utils.timezone import now
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
from users.models import Member, Department, StudentVolunteer
import datetime
from utils.fields import CustomRichTextField
from . import models as initiative_models


def validate_future_date(value):
    if value < datetime.date.today():
        raise ValidationError('Date cannot be in the past')

def validate_file_size(value):
    filesize = value.size
    if filesize > 10 * 1024 * 1024:  # 10MB limit
        raise ValidationError("Maximum file size is 10MB")

class Initiative(models.Model):
    STATUS_CHOICES = [
        ('PLANNED', 'Planned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('ON_HOLD', 'On Hold'),
        ('CANCELLED', 'Cancelled')
    ]

    SDG_CHOICES = [
        ('SDG_1', 'No Poverty'),
        ('SDG_2', 'Zero Hunger'),
        ('SDG_3', 'Good Health and Well-being'),
        ('SDG_4', 'Quality Education'),
        ('SDG_5', 'Gender Equality'),
        ('SDG_6', 'Clean Water and Sanitation'),
        ('SDG_7', 'Affordable and Clean Energy'),
        ('SDG_8', 'Decent Work and Economic Growth'),
        ('SDG_9', 'Industry, Innovation and Infrastructure'),
        ('SDG_10', 'Reduced Inequalities'),
        ('SDG_11', 'Sustainable Cities and Communities'),
        ('SDG_12', 'Responsible Consumption and Production'),
        ('SDG_13', 'Climate Action'),
        ('SDG_14', 'Life Below Water'),
        ('SDG_15', 'Life on Land'),
        ('SDG_16', 'Peace, Justice and Strong Institutions'),
        ('SDG_17', 'Partnerships for the Goals')
    ]

    name = models.CharField(max_length=255, unique=True)
    description = CustomRichTextField()
    start_date = models.DateField(help_text="Format: YYYY-MM-DD")
    end_date = models.DateField(help_text="Format: YYYY-MM-DD")
    budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    actual_spend = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    stakeholders = models.ManyToManyField('Stakeholder', related_name='initiatives',blank=True)
    created_by = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='created_initiatives')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='initiatives')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNED')
    sdg_alignment = models.CharField(max_length=50, choices=SDG_CHOICES)
    target_beneficiaries = models.TextField(help_text="Describe the target groups and expected impact")
    success_metrics = models.TextField(help_text="Define how success will be measured")
    challenges_faced = models.TextField(blank=True)
    lessons_learned = models.TextField(blank=True)
    attachments = models.FileField(
        upload_to='initiative_docs/',
        blank=True,
        validators=[validate_file_size]
    )
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    volunteer = models.ManyToManyField("users.StudentVolunteer", related_name='initiatives')
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['start_date']),
            models.Index(fields=['sdg_alignment'])
        ]
    
    def clean(self):
        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                raise ValidationError('End date must be after start date')
        if self.actual_spend > self.budget:
            raise ValidationError('Actual spend cannot exceed budget')

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

class BrainstormingSession(models.Model):
    SESSION_TYPES = [
        ('INTERNAL', 'Internal Team'),
        ('COMMUNITY', 'Community Leaders'),
        ('STAKEHOLDER', 'Stakeholder Workshop'),
        ('FGD', 'Focus Group Discussion')
    ]

    initiative = models.ForeignKey(Initiative, on_delete=models.CASCADE, related_name='brainstorming_sessions')
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES)
    date = models.DateField()
    location = models.CharField(max_length=255)
    facilitator = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='facilitated_sessions')
    participants_count = models.PositiveIntegerField()
    agenda = CustomRichTextField()
    summary = CustomRichTextField()
    key_outcomes = CustomRichTextField()
    next_steps = CustomRichTextField()
    notes = models.TextField(blank=True)
    materials_used = models.TextField(blank=True, help_text="List materials used in the session")
    attachments = models.FileField(
        upload_to='brainstorming_docs/',
        blank=True,
        validators=[validate_file_size]
    )
    feedback_summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_session_type_display()} for {self.initiative.name}"

class CommunityFeedback(models.Model):
    FEEDBACK_TYPES = [
        ('SURVEY', 'Survey Response'),
        ('SUGGESTION', 'Suggestion Box'),
        ('VERBAL', 'Verbal Feedback'),
        ('ONLINE', 'Online Portal')
    ]

    initiative = models.ForeignKey(Initiative, on_delete=models.CASCADE, related_name='community_feedback')
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    feedback_date = models.DateField(auto_now_add=True)
    feedback_text = CustomRichTextField()
    submitted_by = models.CharField(max_length=100, blank=True, help_text="Optional: Name of person providing feedback")
    contact_info = models.CharField(max_length=100, blank=True, help_text="Optional: Contact information")
    category = models.CharField(max_length=100, help_text="Category of feedback (e.g., Services, Facilities)")
    priority = models.CharField(
        max_length=20,
        choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High')],
        default='MEDIUM'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('NEW', 'New'),
            ('IN_REVIEW', 'In Review'),
            ('ADDRESSED', 'Addressed'),
            ('CLOSED', 'Closed')
        ],
        default='NEW'
    )
    assigned_to = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_feedback'
    )
    response_text = models.TextField(blank=True)
    response_date = models.DateField(null=True, blank=True)
    is_anonymous = models.BooleanField(default=False)

    def __str__(self):
        return f"Feedback for {self.initiative.name} - {self.feedback_date}"

class NeedsAnalysis(models.Model):
    initiative = models.ForeignKey(Initiative, on_delete=models.CASCADE, related_name='needs_analyses')
    target_group = models.CharField(max_length=100)
    identified_need = CustomRichTextField()
    priority_level = models.CharField(
        max_length=20,
        choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High')],
        default='MEDIUM'
    )
    current_services = models.TextField(help_text="Describe existing services addressing this need")
    service_gaps = models.TextField(help_text="Identify gaps in current services")
    proposed_solution = CustomRichTextField()
    required_resources = CustomRichTextField()
    estimated_budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    implementation_timeline = CustomRichTextField()
    success_indicators = CustomRichTextField()
    data_sources = models.TextField(help_text="Sources of information for this analysis")
    created_by = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='created_analyses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Needs Analysis for {self.initiative.name} - {self.target_group}"

class CommunityMapping(models.Model):
    initiative = models.ForeignKey(Initiative, on_delete=models.CASCADE, related_name='community_mappings')
    area_name = models.CharField(max_length=255)
    population_size = models.PositiveIntegerField()
    demographic_data = models.TextField(help_text="Detailed breakdown of community demographics")
    existing_services = models.TextField(help_text="List of current services in the area")
    key_stakeholders = models.TextField(help_text="Important community leaders and organizations")
    challenges = models.TextField(help_text="Main challenges faced by the community")
    opportunities = models.TextField(help_text="Potential opportunities for intervention")
    resources_available = CustomRichTextField()
    map_file = models.FileField(
        upload_to='community_maps/',
        blank=True,
        validators=[validate_file_size]
    )
    mapped_by = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='mapped_communities')
    mapping_date = models.DateField()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Community Mapping - {self.area_name}"

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent')
    ]
    
    STATUS_CHOICES = [
        ('TODO', 'To Do'),
        ('IN_PROGRESS', 'In Progress'),
        ('REVIEW', 'Under Review'),
        ('COMPLETED', 'Completed'),
        ('ON_HOLD', 'On Hold')
    ]
    
    initiative = models.ForeignKey(
        Initiative, 
        on_delete=models.CASCADE, 
        related_name='initiative_tasks'  # Changed to avoid conflict
    )
    
    milestone = models.ForeignKey(
        'initiatives.Milestone',
        on_delete=models.SET_NULL,  # Changed to SET_NULL to prevent data loss
        related_name='milestone_tasks',  # Changed to avoid conflict
        null=True,
        blank=True
    )
    
    title = models.CharField(
        max_length=255,
        help_text="Enter the task title"
    )
    
    description = CustomRichTextField(
        blank=True,
        help_text="Detailed description of the task"
    )
    
    assigned_to = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,  # Changed to SET_NULL for better data integrity
        related_name='assigned_tasks',
        null=True,
        blank=True
    )
    
    priority = models.CharField(
        max_length=20, 
        choices=PRIORITY_CHOICES, 
        default='MEDIUM'
    )
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='TODO'
    )
    
    start_date = models.DateField(
        help_text="When should this task begin?"
    )
    
    due_date = models.DateField(
        help_text="When should this task be completed?"
    )
    
    completion_date = models.DateField(
        null=True, 
        blank=True
    )
    
    progress = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(100)],
        help_text="Progress percentage (0-100)"
    )
    
    comments = models.TextField(
        blank=True,
        help_text="Additional notes or comments about the task"
    )
    
    dependencies = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='dependent_tasks'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', 'priority']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['due_date'])
        ]
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'

    def __str__(self):
        return f"{self.title} - {self.initiative.name}"

    def clean(self):
        errors = {}
        
        # Validate dates
        if self.start_date and self.due_date and self.due_date < self.start_date:
            errors['due_date'] = 'Due date must be after start date'
            
        if self.completion_date:
            if self.completion_date < self.start_date:
                errors['completion_date'] = 'Completion date cannot be before start date'
            if self.status != 'COMPLETED':
                errors['status'] = 'Status must be COMPLETED if completion date is set'
                
        # Validate milestone belongs to same initiative
        if self.milestone and self.initiative:
            if self.milestone.initiative != self.initiative:
                errors['milestone'] = 'Milestone must belong to the same initiative'
                
        # Validate progress and status consistency
        if self.progress == 100 and self.status != 'COMPLETED':
            errors['progress'] = 'Task with 100% progress should be marked as completed'
        if self.status == 'COMPLETED' and self.progress != 100:
            errors['status'] = 'Completed task should have 100% progress'
            
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Auto-update status based on progress
        if self.progress == 0 and self.status == 'TODO':
            pass
        elif self.progress == 100:
            self.status = 'COMPLETED'
            if not self.completion_date:
                self.completion_date = timezone.now().date()
        elif self.progress > 0:
            self.status = 'IN_PROGRESS'
            
        super().save(*args, **kwargs)

    def is_delayed(self):
        """Check if task is delayed"""
        if self.status == 'COMPLETED':
            return False
        return self.due_date < timezone.now().date()

    def days_until_due(self):
        """Calculate days remaining until due date"""
        if self.status == 'COMPLETED':
            return 0
        return (self.due_date - timezone.now().date()).days

    def depends_on(self):
        """Get list of tasks this task depends on"""
        return self.dependencies.all()

    def dependent_tasks(self):
        """Get list of tasks that depend on this task"""
        return self.dependent_tasks.all()

    def can_start(self):
        """Check if all dependencies are completed"""
        return not self.dependencies.exclude(status='COMPLETED').exists()

    def update_progress(self, new_progress):
        """Update progress ensuring proper status changes"""
        self.progress = min(100, max(0, new_progress))
        self.save()

class Stakeholder(models.Model):
    STAKEHOLDER_TYPES = [
        ('NGO', 'Non-Governmental Organization'),
        ('GOVT', 'Government Body'),
        ('CORP', 'Corporate Partner'),
        ('COMM', 'Community Organization'),
        ('ACAD', 'Academic Institution')
    ]

    name = models.CharField(max_length=255)
    organization_type = models.CharField(max_length=20, choices=STAKEHOLDER_TYPES)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = CustomRichTextField()
    involvement_level = models.CharField(
        max_length=20,
        choices=[('HIGH', 'High'), ('MEDIUM', 'Medium'), ('LOW', 'Low')],
        default='MEDIUM'
    )
    resources_provided = models.TextField(blank=True)
    expectations = models.TextField(blank=True)
    contribution_type = models.TextField(help_text="How the stakeholder contributes to initiatives")
    notes = models.TextField(blank=True)
    last_contact = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.get_organization_type_display()}"

class Event(models.Model):
    EVENT_STATUS_CHOICES = [
        ('PLANNED', 'Planned'),
        ('CONFIRMED', 'Confirmed'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled')
    ]

    EVENT_TYPES = [
        ('WORKSHOP', 'Workshop'),
        ('SEMINAR', 'Seminar'),
        ('TRAINING', 'Training'),
        ('COMMUNITY', 'Community Event'),
        ('MEETING', 'Stakeholder Meeting')
    ]

    initiative = models.ForeignKey(Initiative, on_delete=models.CASCADE, related_name='events')
    name = models.CharField(max_length=255)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    description = CustomRichTextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=255)
    virtual_meeting_link = models.URLField(blank=True)
    organizer = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='organized_events')
    status = models.CharField(max_length=20, choices=EVENT_STATUS_CHOICES, default='PLANNED')
    max_participants = models.PositiveIntegerField()
    current_participants = models.PositiveIntegerField(default=0)
    agenda = CustomRichTextField()
    resources_needed = CustomRichTextField()
    budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    actual_spend = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    feedback_summary = models.TextField(blank=True)
    materials = models.FileField(
        upload_to='event_materials/' ,
        blank=True ,
        validators=[validate_file_size]
    )
    speakers = models.ManyToManyField(Member , related_name='speaking_events' , blank=True)
    volunteers = models.ManyToManyField(StudentVolunteer , related_name='volunteered_events' , blank=True)
    photos = models.FileField(
        upload_to='event_photos/' ,
        blank=True ,
        validators=[validate_file_size]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['status']) ,
            models.Index(fields=['start_date']) ,
            models.Index(fields=['event_type'])
        ]

    def __str__(self):
        return f"{self.name} ({self.start_date})"

    def clean(self):
        if self.end_date <= self.start_date:
            raise ValidationError('End date must be after start date')
        if self.current_participants > self.max_participants:
            raise ValidationError('Current participants cannot exceed maximum participants')
        if self.actual_spend > self.budget:
            raise ValidationError('Actual spend cannot exceed budget')

    def is_full(self):
        return self.current_participants >= self.max_participants

    def registration_open(self):
        return not self.is_full() and self.status == 'CONFIRMED'


class Feedback(models.Model):
    RATING_CHOICES = [(i , i) for i in range(1 , 6)]

    event = models.ForeignKey(Event , on_delete=models.CASCADE , related_name='feedback_entries')
    participant_name = models.CharField(max_length=100 , blank=True)
    email = models.EmailField(blank=True)
    rating = models.IntegerField(choices=RATING_CHOICES)
    feedback_text = CustomRichTextField()
    suggestions = models.TextField(blank=True)
    would_recommend = models.BooleanField(default=True)
    areas_of_improvement = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['rating']) ,
            models.Index(fields=['submitted_at'])
        ]

    def __str__(self):
        if self.is_anonymous:
            return f"Anonymous Feedback - {self.event.name}"
        return f"Feedback from {self.participant_name} - {self.event.name}"


class Risk(models.Model):
    RISK_LEVELS = [
        ('LOW' , 'Low') ,
        ('MEDIUM' , 'Medium') ,
        ('HIGH' , 'High') ,
        ('CRITICAL' , 'Critical')
    ]

    RISK_TYPES = [
        ('FINANCIAL' , 'Financial Risk') ,
        ('OPERATIONAL' , 'Operational Risk') ,
        ('STRATEGIC' , 'Strategic Risk') ,
        ('COMPLIANCE' , 'Compliance Risk') ,
        ('REPUTATION' , 'Reputational Risk') ,
        ('SAFETY' , 'Safety Risk')
    ]

    initiative = models.ForeignKey(Initiative , on_delete=models.CASCADE , related_name='risks')
    risk_type = models.CharField(max_length=20 , choices=RISK_TYPES)
    description = models.TextField(blank=True, help_text="Describe the risk in detail")
    risk_level = models.CharField(max_length=20 , choices=RISK_LEVELS)
    probability = models.IntegerField(
        validators=[MinValueValidator(1) , MaxValueValidator(5)] ,
        help_text="1 (Very Unlikely) to 5 (Very Likely)"
    )
    impact = models.IntegerField(
        validators=[MinValueValidator(1) , MaxValueValidator(5)] ,
        help_text="1 (Minimal Impact) to 5 (Severe Impact)"
    )
    mitigation_plan = CustomRichTextField()
    contingency_plan = CustomRichTextField()
    owner = models.ForeignKey(Member , on_delete=models.CASCADE , related_name='owned_risks')
    status = models.CharField(
        max_length=20 ,
        choices=[
            ('IDENTIFIED' , 'Identified') ,
            ('ASSESSED' , 'Assessed') ,
            ('MITIGATED' , 'Mitigated') ,
            ('CLOSED' , 'Closed') ,
            ('OCCURRED' , 'Risk Occurred')
        ] ,
        default='IDENTIFIED'
    )
    review_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-risk_level' , '-probability']
        indexes = [
            models.Index(fields=['risk_level']) ,
            models.Index(fields=['status'])
        ]

    def __str__(self):
        return f"{self.get_risk_type_display()} - {self.initiative.name}"

    def risk_score(self):
        return self.probability * self.impact


class KPI(models.Model):
    FREQUENCY_CHOICES = [
        ('DAILY' , 'Daily') ,
        ('WEEKLY' , 'Weekly') ,
        ('MONTHLY' , 'Monthly') ,
        ('QUARTERLY' , 'Quarterly') ,
        ('YEARLY' , 'Yearly')
    ]

    initiative = models.ForeignKey(Initiative , on_delete=models.CASCADE , related_name='kpis')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    target_value = models.FloatField(validators=[MinValueValidator(0.0)])
    current_value = models.FloatField(default=0 , validators=[MinValueValidator(0.0)])
    unit_of_measure = models.CharField(blank=True,max_length=50)
    measurement_frequency = models.CharField(max_length=20 , choices=FREQUENCY_CHOICES)
    data_source = models.TextField(help_text="Where and how is this KPI measured?")
    responsible_person = models.ForeignKey(Member , on_delete=models.CASCADE , related_name='monitored_kpis')
    baseline_value = models.FloatField(null=True,blank=True,validators=[MinValueValidator(0.0)])
    target_date = models.DateField()
    achieved = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "KPI"
        verbose_name_plural = "KPIs"
        ordering = ['name']
        indexes = [
            models.Index(fields=['achieved']) ,
            models.Index(fields=['measurement_frequency'])
        ]

    def __str__(self):
        return f"{self.name} - {self.initiative.name}"

    def achievement_percentage(self):
        if self.target_value == 0:
            return 0
        return (self.current_value / self.target_value) * 100

    def save(self , *args , **kwargs):
        self.achieved = self.current_value >= self.target_value
        super().save(*args , **kwargs)


class Milestone(models.Model):
    initiative = models.ForeignKey(Initiative , on_delete=models.CASCADE , related_name='milestones')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    target_date = models.DateField()
    actual_completion_date = models.DateField(null=True , blank=True)
    status = models.CharField(
        max_length=20 ,
        choices=[
            ('PENDING' , 'Pending') ,
            ('IN_PROGRESS' , 'In Progress') ,
            ('COMPLETED' , 'Completed') ,
            ('DELAYED' , 'Delayed')
        ] ,
        default='PENDING'
    )
    deliverables = models.TextField(blank=True)
    dependencies = models.ManyToManyField('self' , blank=True , symmetrical=False)
    responsible_person = models.ForeignKey(Member , on_delete=models.CASCADE , related_name='responsible_milestones')
    progress = models.IntegerField(
        default=0 ,
        validators=[MinValueValidator(0) , MaxValueValidator(100)]
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['target_date']
        indexes = [
            models.Index(fields=['status']) ,
            models.Index(fields=['target_date'])
        ]

    def __str__(self):
        return f"{self.title} - {self.initiative.name}"

    def is_delayed(self):
        return (not self.actual_completion_date and
                self.target_date < datetime.date.today())


class Budget(models.Model):
    BUDGET_TYPES = [
        ('OPERATIONAL' , 'Operational') ,
        ('CAPITAL' , 'Capital') ,
        ('PROGRAM' , 'Program') ,
        ('EMERGENCY' , 'Emergency')
    ]

    initiative = models.ForeignKey(Initiative , on_delete=models.CASCADE , related_name='budget_items')
    budget_type = models.CharField(max_length=20 , choices=BUDGET_TYPES)
    item_name = models.CharField(max_length=255)
    description = CustomRichTextField()
    estimated_amount = models.DecimalField(
        max_digits=10 ,
        decimal_places=2 ,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    actual_amount = models.DecimalField(
        max_digits=10 ,
        decimal_places=2 ,
        default=Decimal('0.00') ,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    quantity = models.PositiveIntegerField(default=1)
    unit_cost = models.DecimalField(null=True ,blank=True,
        max_digits=10 ,
        decimal_places=2 ,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    variance_explanation = models.TextField(blank=True)
    date_required = models.DateField()
    approved_by = models.ForeignKey(
        Member ,
        on_delete=models.SET_NULL ,
        null=True ,
        related_name='initiative_approved_budgets'  # Changed from 'approved_budgets'
    )
    approval_date = models.DateField(null=True , blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date_required']
        indexes = [
            models.Index(fields=['budget_type']) ,
            models.Index(fields=['date_required'])
        ]

    def __str__(self):
        return f"{self.item_name} - {self.initiative.name}"

    def variance_amount(self):
        return self.actual_amount - self.estimated_amount

    def variance_percentage(self):
        if self.estimated_amount == 0:
            return 0
        return (self.variance_amount() / self.estimated_amount) * 100


class ExecutionLog(models.Model):
    initiative = models.ForeignKey(Initiative , on_delete=models.CASCADE , related_name='execution_logs')
    date = models.DateField()
    activity = CustomRichTextField()
    outcomes = CustomRichTextField()
    challenges = models.TextField(blank=True)
    participants = models.ManyToManyField(Member , related_name='participated_activities')
    photos = models.FileField(
        upload_to='execution_photos/' ,
        blank=True ,
        validators=[validate_file_size]
    )
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        Member ,
        on_delete=models.CASCADE ,
        related_name='created_logs'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date'])
        ]

    def __str__(self):
        return f"Execution Log - {self.initiative.name} ({self.date})"