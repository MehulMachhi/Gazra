from django.db import models

# Create your models here.
# sustainability/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.timezone import now
from decimal import Decimal
from users.models import Member
from initiatives.models import Initiative
from utils.fields import CustomRichTextField


class ReplicableProgram(models.Model):
    PROGRAM_CATEGORIES = [
        ('WORKSHOP', 'Workshop Series'),
        ('TRAINING', 'Training Program'),
        ('OUTREACH', 'Outreach Campaign'),
        ('MENTORSHIP', 'Mentorship Program'),
        ('SKILL_DEV', 'Skill Development')
    ]

    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PILOTING', 'Piloting'),
        ('VALIDATED', 'Validated'),
        ('READY', 'Ready for Replication'),
        ('ACTIVE', 'Actively Replicated')
    ]

    name = models.CharField(max_length=255)
    initiative = models.ForeignKey(
        Initiative,
        on_delete=models.CASCADE,
        related_name='replicable_programs'
    )
    program_category = models.CharField(max_length=20, choices=PROGRAM_CATEGORIES)
    description = CustomRichTextField(blank=True)
    objectives = CustomRichTextField(blank=True)
    target_group = CustomRichTextField(blank=True)
    key_activities = CustomRichTextField(blank=True)
    resources_required = CustomRichTextField(blank=True)
    implementation_guide = CustomRichTextField(blank=True)
    success_metrics = models.JSONField()
    training_materials = models.FileField(
        upload_to='program_materials/',
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )
    developed_by = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='developed_programs'
    )
    replication_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    timeline = models.JSONField(
        help_text="JSON object containing implementation timeline"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.get_program_category_display()}"

class ProgramReplication(models.Model):
    STATUS_CHOICES = [
        ('PLANNED', 'Planned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('SUSPENDED', 'Suspended')
    ]

    replicable_program = models.ForeignKey(
        ReplicableProgram,
        on_delete=models.CASCADE,
        related_name='replications'
    )
    location = models.CharField(max_length=255)
    implementing_partner = CustomRichTextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    participants_count = models.IntegerField(default=0)
    budget_allocated = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    actual_spent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    success_metrics_achieved = models.JSONField(default=dict)
    challenges_faced = models.TextField(blank=True)
    learnings = models.TextField(blank=True)
    supporting_documents = models.FileField(
        upload_to='replication_docs/',
        blank=True
    )
    coordinator = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='coordinated_replications'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.replicable_program.name} at {self.location}"

class CorporatePartner(models.Model):
    PARTNER_CATEGORIES = [
        ('CSR', 'CSR Partner'),
        ('TECHNICAL', 'Technical Partner'),
        ('FUNDING', 'Funding Partner'),
        ('IMPLEMENTATION', 'Implementation Partner')
    ]

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=PARTNER_CATEGORIES)
    csr_focus_areas = CustomRichTextField(blank=True)
    contact_person = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = CustomRichTextField(blank=True)
    partnership_history = CustomRichTextField(blank=True)
    total_funding = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    current_engagement = CustomRichTextField(blank=True)
    branding_requirements = CustomRichTextField(blank=True)
    mou_document = models.FileField(
        upload_to='partner_docs/',
        blank=True
    )
    relationship_manager = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,
        null=True,
        related_name='managed_partners'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

class FundingProposal(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('UNDER_REVIEW', 'Under Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected')
    ]

    title = models.CharField(max_length=255)
    corporate_partner = models.ForeignKey(
        CorporatePartner,
        on_delete=models.CASCADE,
        related_name='funding_proposals'
    )
    initiative = models.ForeignKey(
        Initiative,
        on_delete=models.CASCADE,
        related_name='funding_proposals'
    )
    amount_requested = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    executive_summary = CustomRichTextField(blank=True)
    sdg_alignment = CustomRichTextField(blank=True)
    program_details = CustomRichTextField(blank=True)
    budget_breakdown = models.JSONField()
    impact_metrics = models.JSONField()
    timeline = models.JSONField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )
    submission_date = models.DateField(null=True, blank=True)
    feedback_received = CustomRichTextField(blank=True)
    proposal_document = models.FileField(
        upload_to='proposals/',
        blank=True
    )
    prepared_by = models.ForeignKey(
        Member ,
        on_delete=models.CASCADE ,
        related_name='sustainability_prepared_proposals'  # Changed from 'prepared_proposals'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.corporate_partner.name}"

class AnnualBudget(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('REVIEW', 'Under Review'),
        ('APPROVED', 'Approved'),
        ('ACTIVE', 'Active'),
        ('CLOSED', 'Closed')
    ]

    fiscal_year = models.CharField(max_length=10)
    total_budget = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    staff_salaries = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    operational_costs = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    program_costs = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    marketing_costs = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    contingency_fund = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    detailed_breakdown = models.JSONField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )
    notes = CustomRichTextField(blank=True)
    prepared_by = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='prepared_budgets'
    )
    approved_by = models.ForeignKey(
        Member ,
        on_delete=models.SET_NULL ,
        null=True ,
        related_name='annual_approved_budgets'  # Changed from 'approved_budgets'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Annual Budget {self.fiscal_year}"

class BudgetTracking(models.Model):
    annual_budget = models.ForeignKey(
        AnnualBudget,
        on_delete=models.CASCADE,
        related_name='tracking_records'
    )
    month = models.DateField()
    category = models.CharField(max_length=50)
    budgeted_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    actual_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    variance_explanation = CustomRichTextField(blank=True)
    recorded_by = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='budget_records'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {self.month}"

class FranchiseModel(models.Model):
    STATUS_CHOICES = [
        ('DEVELOPMENT', 'In Development'),
        ('PILOTING', 'Piloting'),
        ('ACTIVE', 'Active'),
        ('SUSPENDED', 'Suspended')
    ]

    name = models.CharField(max_length=255)
    description = CustomRichTextField(blank=True)
    operational_guidelines = CustomRichTextField(blank=True)
    training_modules = models.JSONField()
    branding_guidelines = CustomRichTextField(blank=True)
    setup_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    revenue_model = CustomRichTextField(blank=True)
    support_services = CustomRichTextField(blank=True)
    legal_requirements = CustomRichTextField(blank=True)
    franchise_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    royalty_structure = CustomRichTextField(blank=True)
    toolkit_documents = models.FileField(
        upload_to='franchise_docs/',
        blank=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DEVELOPMENT'
    )
    developed_by = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='developed_franchises'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} Franchise Model"

class FranchiseLocation(models.Model):
    STATUS_CHOICES = [
        ('SETUP', 'Setup Phase'),
        ('TRAINING', 'Training Phase'),
        ('OPERATIONAL', 'Operational'),
        ('SUSPENDED', 'Suspended')
    ]

    franchise_model = models.ForeignKey(
        FranchiseModel,
        on_delete=models.CASCADE,
        related_name='locations'
    )
    location_name = models.CharField(max_length=255)
    partner_organization = models.CharField(max_length=255)
    address = CustomRichTextField(blank=True)
    launch_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='SETUP'
    )
    employees_count = models.IntegerField(default=0)
    monthly_revenue = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    performance_metrics = models.JSONField(default=dict)
    mentor = models.ForeignKey(
        Member,
        on_delete=models.SET_NULL,
        null=True,
        related_name='mentored_locations'
    )
    feedback = CustomRichTextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.franchise_model.name} - {self.location_name}"

class Product(models.Model):
    PRODUCT_TYPES = [
        ('FOOD', 'Food Item'),
        ('BEVERAGE', 'Beverage'),
        ('MERCHANDISE', 'Merchandise'),
        ('SERVICE', 'Service')
    ]

    name = models.CharField(max_length=255)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES)
    description = CustomRichTextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    cost_price = models.DecimalField(max_digits=8, decimal_places=2)
    available_channels = CustomRichTextField(blank=True)
    stock_quantity = models.IntegerField(default=0)
    image = models.ImageField(
        upload_to='product_images/',
        blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_product_type_display()})"


# sustainability/models.py (continued)

class ConsultingService(models.Model):
    SERVICE_TYPES = [
        ('SETUP', 'Enterprise Setup'),
        ('TRAINING', 'Training Workshop'),
        ('CONSULTING', 'Consulting Package'),
        ('MENTORING', 'Mentoring Program')
    ]

    title = models.CharField(max_length=255)  # Changed from 'name' to 'title'
    service_type = models.CharField(
        max_length=20,
        choices=SERVICE_TYPES
    )
    description = CustomRichTextField(blank=True)
    duration = models.CharField(max_length=100)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    deliverables = CustomRichTextField(blank=True)
    target_audience = CustomRichTextField(blank=True)
    prerequisites = CustomRichTextField(blank=True)
    materials_included = CustomRichTextField(blank=True)
    consultant = models.ForeignKey(
        'users.Member',
        on_delete=models.CASCADE,
        related_name='consulting_services'
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.get_service_type_display()})"


class ConsultingEngagement(models.Model):
    STATUS_CHOICES = [
        ('PLANNED' , 'Planned') ,
        ('IN_PROGRESS' , 'In Progress') ,
        ('COMPLETED' , 'Completed') ,
        ('CANCELLED' , 'Cancelled')
    ]

    service = models.ForeignKey(
        ConsultingService ,
        on_delete=models.CASCADE ,
        related_name='engagements'
    )
    client_name = models.CharField(max_length=255)
    client_organization = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20 ,
        choices=STATUS_CHOICES ,
        default='PLANNED'
    )
    contract_value = models.DecimalField(
        max_digits=10 ,
        decimal_places=2
    )
    payment_status = models.CharField(
        max_length=20 ,
        choices=[
            ('PENDING' , 'Pending') ,
            ('PARTIAL' , 'Partially Paid') ,
            ('COMPLETED' , 'Fully Paid')
        ]
    )
    deliverables_status = models.JSONField(
        help_text="JSON object tracking deliverable completion"
    )
    feedback = CustomRichTextField(blank=True)
    satisfaction_rating = models.IntegerField(
        validators=[MinValueValidator(1) , MaxValueValidator(5)] ,
        null=True ,
        blank=True
    )
    consultant = models.ForeignKey(
        Member ,
        on_delete=models.CASCADE ,
        related_name='consulting_engagements'
    )
    contract_document = models.FileField(
        upload_to='consulting_contracts/' ,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.service.name} - {self.client_organization}"


class SocialEnterpriseMetrics(models.Model):
    METRIC_TYPES = [
        ('FINANCIAL' , 'Financial Metrics') ,
        ('IMPACT' , 'Impact Metrics') ,
        ('OPERATIONAL' , 'Operational Metrics')
    ]

    metric_type = models.CharField(max_length=20 , choices=METRIC_TYPES)
    report_date = models.DateField()
    # Product Sales Metrics
    total_product_revenue = models.DecimalField(
        max_digits=12 ,
        decimal_places=2 ,
        default=Decimal('0.00')
    )
    total_products_sold = models.IntegerField(default=0)
    best_selling_products = models.JSONField(
        help_text="JSON object containing top selling products"
    )

    # Consulting Metrics
    consulting_revenue = models.DecimalField(
        max_digits=12 ,
        decimal_places=2 ,
        default=Decimal('0.00')
    )
    engagements_completed = models.IntegerField(default=0)
    client_satisfaction = models.FloatField(
        validators=[MinValueValidator(0.0) , MaxValueValidator(5.0)] ,
        null=True ,
        blank=True
    )

    # Franchise Metrics
    franchise_revenue = models.DecimalField(
        max_digits=12 ,
        decimal_places=2 ,
        default=Decimal('0.00')
    )
    active_franchises = models.IntegerField(default=0)
    franchise_performance = models.JSONField(
        help_text="JSON object containing franchise performance data"
    )

    # Overall Impact
    jobs_created = models.IntegerField(default=0)
    beneficiaries_impacted = models.IntegerField(default=0)
    social_return = CustomRichTextField(blank=True)

    notes = CustomRichTextField(blank=True)
    recorded_by = models.ForeignKey(
        Member ,
        on_delete=models.CASCADE ,
        related_name='recorded_metrics'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-report_date']
        verbose_name_plural = 'Social Enterprise Metrics'

    def __str__(self):
        return f"{self.get_metric_type_display()} Report - {self.report_date}"


class SustainabilityReport(models.Model):
    REPORT_TYPES = [
        ('MONTHLY' , 'Monthly Report') ,
        ('QUARTERLY' , 'Quarterly Report') ,
        ('ANNUAL' , 'Annual Report')
    ]

    report_type = models.CharField(max_length=20 , choices=REPORT_TYPES)
    period_start = models.DateField()
    period_end = models.DateField()

    # Financial Sustainability
    revenue_streams = models.JSONField(
        help_text="JSON object containing revenue breakdown"
    )
    total_revenue = models.DecimalField(
        max_digits=12 ,
        decimal_places=2
    )
    total_expenses = models.DecimalField(
        max_digits=12 ,
        decimal_places=2
    )
    financial_sustainability_ratio = models.FloatField()

    # Program Sustainability
    active_programs = models.IntegerField()
    program_metrics = models.JSONField(
        help_text="JSON object containing program performance data"
    )
    replication_status = models.JSONField(
        help_text="JSON object containing replication progress"
    )

    # Partnership Sustainability
    active_partnerships = models.IntegerField()
    partnership_value = models.DecimalField(
        max_digits=12 ,
        decimal_places=2
    )
    partner_satisfaction = models.FloatField(
        validators=[MinValueValidator(0.0) , MaxValueValidator(5.0)]
    )

    # Impact Sustainability
    beneficiaries_reached = models.IntegerField()
    impact_metrics = models.JSONField(
        help_text="JSON object containing impact data"
    )
    community_feedback = CustomRichTextField(blank=True)

    # Future Planning
    growth_projections = CustomRichTextField(blank=True)
    sustainability_initiatives = CustomRichTextField(blank=True)
    risk_assessment = CustomRichTextField(blank=True)

    # Meta Information
    prepared_by = models.ForeignKey(
        Member ,
        on_delete=models.CASCADE ,
        related_name='sustainability_reports'
    )
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
    report_file = models.FileField(
        upload_to='sustainability_reports/' ,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-period_end']
        unique_together = ['report_type' , 'period_start' , 'period_end']

    def __str__(self):
        return f"{self.get_report_type_display()} Sustainability Report - {self.period_start} to {self.period_end}"