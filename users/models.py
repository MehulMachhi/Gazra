# users/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator , MaxValueValidator , EmailValidator , FileExtensionValidator
from django.utils.timezone import now
from datetime import date
from django.core.exceptions import ValidationError

from utils.fields import CustomRichTextField


def validate_future_end_date(value):
    if value < date.today():
        raise ValidationError('End date cannot be in the past')


def validate_file_size(value):
    filesize = value.size
    if filesize > 5 * 1024 * 1024:  # 5MB limit
        raise ValidationError("Maximum file size is 5MB")


class Member(models.Model):
    MEMBER_TYPES = (
        ('ASSOCIATE' , 'Associate Member') ,
        ('REGULAR' , 'Regular Member') ,
        ('SENIOR' , 'Senior Member') ,
        ('HONORARY' , 'Honorary Member') ,
    )

    STATUS_CHOICES = (
        ('ACTIVE' , 'Active') ,
        ('INACTIVE' , 'Inactive') ,
        ('SUSPENDED' , 'Suspended') ,
        ('ALUMNI' , 'Alumni') ,
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL ,
        on_delete=models.CASCADE ,
        related_name='member_profile'
    )
    member_type = models.CharField(max_length=20 , choices=MEMBER_TYPES)
    join_date = models.DateField(default=now)
    skills = models.TextField(blank=True , help_text="Comma-separated list of skills")
    certifications = models.TextField(blank=True , help_text="List relevant certifications with dates")
    status = models.CharField(
        max_length=20 ,
        choices=STATUS_CHOICES ,
        default='ACTIVE'
    )
    bio = models.TextField(blank=True , help_text="Brief introduction about yourself")
    linkedin_profile = models.URLField(blank=True)
    github_profile = models.URLField(blank=True)
    profile_picture = models.ImageField(
        upload_to='member_profiles/' ,
        blank=True ,
        validators=[validate_file_size]
    )
    phone_number = models.CharField(max_length=15 , blank=True)
    emergency_contact = models.CharField(max_length=100 , blank=True)
    emergency_phone = models.CharField(max_length=15 , blank=True)
    last_active = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-join_date']
        indexes = [
            models.Index(fields=['member_type']) ,
            models.Index(fields=['status']) ,
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_member_type_display()}"

    def active_committee_roles(self):
        return self.corecommittee_set.filter(term_end__gte=now()).count()

    def years_of_membership(self):
        return (date.today() - self.join_date).days // 365

    def total_initiatives_created(self):
        return self.user.created_initiatives.count()

    def total_events_organized(self):
        return self.user.organized_events.count()


class CoreCommittee(models.Model):
    ROLES = (
        ('CHAIR' , 'Chairperson') ,
        ('VICE_CHAIR' , 'Vice Chairperson') ,
        ('SECRETARY' , 'Secretary') ,
        ('TREASURER' , 'Treasurer') ,
        ('DEPT_HEAD' , 'Department Head') ,
        ('TECHNICAL_LEAD' , 'Technical Lead') ,
        ('EVENT_COORDINATOR' , 'Event Coordinator') ,
        ('PR_COORDINATOR' , 'PR Coordinator') ,
    )

    member = models.ForeignKey(
        Member ,
        on_delete=models.CASCADE ,
        related_name='committee_positions'
    )
    role = models.CharField(max_length=20 , choices=ROLES)
    term_start = models.DateField()
    term_end = models.DateField(validators=[validate_future_end_date])
    responsibilities = models.TextField(blank=True)
    achievements = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    handover_notes = models.TextField(
        blank=True ,
        help_text="Notes for the next person taking this role"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['term_end']
        indexes = [
            models.Index(fields=['role']) ,
            models.Index(fields=['is_active']) ,
        ]
        verbose_name = "Core Committee Member"
        verbose_name_plural = "Core Committee Members"

    def __str__(self):
        return f"{self.member} - {self.get_role_display()}"

    def clean(self):
        if self.term_start and self.term_end:
            if self.term_end <= self.term_start:
                raise ValidationError('Term end must be after term start')

    def term_duration_months(self):
        return ((self.term_end - self.term_start).days // 30)


class Department(models.Model):
    name = models.CharField(max_length=100 , unique=True)
    description = CustomRichTextField(blank=True)
    head = models.ForeignKey(
        Member ,
        on_delete=models.SET_NULL ,
        null=True ,
        related_name='headed_departments'
    )
    established_on = models.DateField()
    vision = CustomRichTextField(blank=True)
    mission = CustomRichTextField(blank=True)
    budget_allocation = models.DecimalField(
        max_digits=10 ,
        decimal_places=2 ,
        default=0.00
    )
    contact_email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_active']) ,
        ]

    def __str__(self):
        return self.name

    def active_volunteers(self):
        return self.student_volunteers.filter(application_date__gte=now()).count()

    def total_initiatives(self):
        # Assuming there's a related_name for initiatives in the Department model
        return self.initiatives.count()


class StudentVolunteer(models.Model):
    SEX_CHOICES = [
        ('M' , 'Male') ,
        ('F' , 'Female') ,
        ('O' , 'Other') ,
    ]

    STATUS_CHOICES = [
        ('PENDING' , 'Pending') ,
        ('APPROVED' , 'Approved') ,
        ('REJECTED' , 'Rejected') ,
        ('ACTIVE' , 'Active') ,
        ('COMPLETED' , 'Completed') ,
    ]

    name = models.CharField(max_length=100)
    address = models.TextField()
    email = models.EmailField(
        unique=True ,
        validators=[EmailValidator()]
    )
    phone_no = models.CharField(max_length=15)
    sex = models.CharField(max_length=1 , choices=SEX_CHOICES)
    university_name = models.CharField(max_length=200)
    current_semester = models.IntegerField(
        validators=[MinValueValidator(1) , MaxValueValidator(12)]
    )
    department = models.ForeignKey(
        Department ,
        on_delete=models.SET_NULL ,
        null=True ,
        related_name='student_volunteers'
    )
    event = models.ForeignKey(
        'initiatives.Event' ,
        on_delete=models.SET_NULL ,
        null=True ,
        blank=True ,
        related_name='student_volunteers'
    )
    initiative = models.ForeignKey(
        'initiatives.Initiative' ,
        on_delete=models.SET_NULL ,
        null=True ,
        blank=True ,
        related_name='student_volunteers'
    )
    work_duration_months = models.IntegerField(
        validators=[MinValueValidator(1) , MaxValueValidator(12)]
    )
    university_permission = models.BooleanField(default=False)
    resume = models.FileField(
        upload_to='student_resumes/' ,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf' , 'doc' , 'docx']) ,
            validate_file_size
        ] ,
        blank=True
    )
    photograph = models.ImageField(
        upload_to='student_photos/' ,
        validators=[validate_file_size] ,
        blank=True
    )
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20 ,
        choices=STATUS_CHOICES ,
        default='PENDING'
    )
    skills = models.TextField(blank=True)
    interests = models.TextField(blank=True)
    availability = models.TextField(
        blank=True ,
        help_text="Specify your available hours and days"
    )
    emergency_contact = models.CharField(max_length=100 , blank=True)
    emergency_phone = models.CharField(max_length=15 , blank=True)
    approved_by = models.ForeignKey(
        Member ,
        on_delete=models.SET_NULL ,
        null=True ,
        blank=True ,
        related_name='approved_volunteers'
    )
    approval_date = models.DateTimeField(null=True , blank=True)
    rejection_reason = models.TextField(blank=True)
    completion_certificate = models.FileField(
        upload_to='completion_certificates/' ,
        blank=True ,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf']) ,
            validate_file_size
        ]
    )

    class Meta:
        verbose_name = "Student Volunteer"
        verbose_name_plural = "Student Volunteers"
        ordering = ['-application_date']
        indexes = [
            models.Index(fields=['status']) ,
            models.Index(fields=['application_date']) ,
        ]

    def __str__(self):
        return f"{self.name} - {self.university_name}"

    def clean(self):
        if self.status == 'APPROVED' and not self.approved_by:
            raise ValidationError('Approved volunteers must have an approver')