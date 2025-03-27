# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator , MaxValueValidator
from django.urls import reverse
from django.utils.text import slugify
import uuid


class Industry(models.Model):
    name = models.CharField(max_length=100 , unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Industries"
        ordering = ['name']

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=100 , unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Company(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True , blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=255 , blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100)
    established_date = models.DateField()
    company_size = models.CharField(max_length=50 , choices=[
        ('1-10' , '1-10 employees') ,
        ('11-50' , '11-50 employees') ,
        ('51-200' , '51-200 employees') ,
        ('201-500' , '201-500 employees') ,
        ('501-1000' , '501-1000 employees') ,
        ('1001+' , '1001+ employees')
    ])
    industry = models.ForeignKey(Industry , on_delete=models.SET_NULL , null=True)
    is_verified = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    logo = models.ImageField(upload_to='company_logos/' , blank=True)
    cover_image = models.ImageField(upload_to='company_covers/' , blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verification_documents = models.FileField(upload_to='verification_docs/' , blank=True)
    company_email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    registration_number = models.CharField(max_length=50 , blank=True)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['-created_at']

    def save(self , *args , **kwargs):
        if not self.slug:
            self.slug = slugify(self.company_name)
        super().save(*args , **kwargs)

    def __str__(self):
        return self.company_name

    def get_absolute_url(self):
        return reverse('company_detail' , kwargs={'slug': self.slug})


class CompanyReview(models.Model):
    company = models.ForeignKey(Company , on_delete=models.CASCADE , related_name='reviews')
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1) , MaxValueValidator(5)])
    title = models.CharField(max_length=200)
    review_text = models.TextField()
    pros = models.TextField()
    cons = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)
    helpful_votes = models.IntegerField(default=0)

    class Meta:
        unique_together = ('company' , 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.company.company_name} - {self.rating} stars"


class JobSeeker(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE)
    slug = models.SlugField(unique=True , blank=True)
    resume = models.FileField(upload_to='resumes/' , blank=True)
    cover_letter_template = models.TextField(blank=True)
    skills = models.ManyToManyField(Skill , through='JobSeekerSkill')
    experience_years = models.DecimalField(max_digits=4 , decimal_places=1)
    education = models.TextField()
    preferred_job_types = models.CharField(max_length=100)
    preferred_locations = models.CharField(max_length=200)
    preferred_industries = models.ManyToManyField(Industry)
    expected_salary = models.DecimalField(max_digits=10 , decimal_places=2 , null=True , blank=True)
    phone = models.CharField(max_length=15)
    linkedin_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    is_available = models.BooleanField(default=True)
    profile_visibility = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self , *args , **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.user.username}-{uuid.uuid4().hex[:6]}")
        super().save(*args , **kwargs)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class JobSeekerSkill(models.Model):
    job_seeker = models.ForeignKey(JobSeeker , on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill , on_delete=models.CASCADE)
    proficiency_level = models.CharField(max_length=20 , choices=[
        ('beginner' , 'Beginner') ,
        ('intermediate' , 'Intermediate') ,
        ('advanced' , 'Advanced') ,
        ('expert' , 'Expert')
    ])
    years_of_experience = models.DecimalField(max_digits=4 , decimal_places=1)

    class Meta:
        unique_together = ('job_seeker' , 'skill')


class Experience(models.Model):
    job_seeker = models.ForeignKey(JobSeeker , on_delete=models.CASCADE , related_name='experiences')
    company_name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True , blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField()

    class Meta:
        ordering = ['-start_date']


class Education(models.Model):
    job_seeker = models.ForeignKey(JobSeeker , on_delete=models.CASCADE , related_name='educations')
    institution = models.CharField(max_length=100)
    degree = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True , blank=True)
    is_current = models.BooleanField(default=False)
    gpa = models.DecimalField(max_digits=3 , decimal_places=2 , null=True , blank=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name_plural = "Education"


class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('FT' , 'Full Time') ,
        ('PT' , 'Part Time') ,
        ('CT' , 'Contract') ,
        ('IN' , 'Internship') ,
        ('RM' , 'Remote') ,
        ('FL' , 'Freelance') ,
        ('TP' , 'Temporary')
    ]

    EXPERIENCE_LEVEL_CHOICES = [
        ('EN' , 'Entry Level') ,
        ('JR' , 'Junior') ,
        ('MD' , 'Mid Level') ,
        ('SR' , 'Senior') ,
        ('LD' , 'Lead') ,
        ('EX' , 'Executive')
    ]

    STATUS_CHOICES = [
        ('DR' , 'Draft') ,
        ('PN' , 'Pending') ,
        ('AC' , 'Active') ,
        ('PS' , 'Paused') ,
        ('CL' , 'Closed') ,
        ('EX' , 'Expired')
    ]

    company = models.ForeignKey(Company , on_delete=models.CASCADE , related_name='jobs')
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True , blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=255)
    requirements = models.TextField()
    responsibilities = models.TextField()
    benefits = models.TextField()
    skills_required = models.ManyToManyField(Skill , related_name='required_for_jobs')
    skills_preferred = models.ManyToManyField(Skill , related_name='preferred_for_jobs')
    job_type = models.CharField(max_length=2 , choices=JOB_TYPE_CHOICES)
    experience_level = models.CharField(max_length=2 , choices=EXPERIENCE_LEVEL_CHOICES)
    experience_years_min = models.IntegerField()
    experience_years_max = models.IntegerField()
    education_requirement = models.CharField(max_length=100)
    industry = models.ForeignKey(Industry , on_delete=models.SET_NULL , null=True)
    location = models.CharField(max_length=100)
    is_remote = models.BooleanField(default=False)
    salary_min = models.DecimalField(max_digits=10 , decimal_places=2)
    salary_max = models.DecimalField(max_digits=10 , decimal_places=2)
    salary_is_negotiable = models.BooleanField(default=False)
    hide_salary = models.BooleanField(default=False)
    status = models.CharField(max_length=2 , choices=STATUS_CHOICES , default='DR')
    is_featured = models.BooleanField(default=False)
    posted_date = models.DateTimeField(default=timezone.now)
    deadline = models.DateTimeField()
    positions_available = models.IntegerField(default=1)
    applications_count = models.IntegerField(default=0)
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self , *args , **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.company.company_name}-{uuid.uuid4().hex[:6]}")
        super().save(*args , **kwargs)

    def __str__(self):
        return f"{self.title} at {self.company.company_name}"

    def get_absolute_url(self):
        return reverse('job_detail' , kwargs={'slug': self.slug})


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('PD' , 'Pending') ,
        ('RV' , 'Reviewing') ,
        ('SC' , 'Shortlisted') ,
        ('IV' , 'Interview Scheduled') ,
        ('AC' , 'Accepted') ,
        ('RJ' , 'Rejected') ,
        ('WD' , 'Withdrawn')
    ]

    job = models.ForeignKey(Job , on_delete=models.CASCADE , related_name='applications')
    applicant = models.ForeignKey(JobSeeker , on_delete=models.CASCADE , related_name='applications')
    resume = models.FileField(upload_to='application_resumes/' , blank=True)
    cover_letter = models.TextField()
    status = models.CharField(max_length=2 , choices=STATUS_CHOICES , default='PD')
    applied_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_viewed = models.BooleanField(default=False)
    viewed_date = models.DateTimeField(null=True , blank=True)
    notes = models.TextField(blank=True)
    expected_salary = models.DecimalField(max_digits=10 , decimal_places=2 , null=True , blank=True)
    reference = models.CharField(max_length=100 , blank=True)

    class Meta:
        unique_together = ('job' , 'applicant')
        ordering = ['-applied_date']

    def __str__(self):
        return f"{self.applicant.user.get_full_name()} - {self.job.title}"


class JobAlert(models.Model):
    FREQUENCY_CHOICES = [
        ('D' , 'Daily') ,
        ('W' , 'Weekly') ,
        ('M' , 'Monthly')
    ]

    user = models.ForeignKey(User , on_delete=models.CASCADE , related_name='job_alerts')
    keywords = models.CharField(max_length=200)
    location = models.CharField(max_length=100 , blank=True)
    job_type = models.CharField(max_length=2 , choices=Job.JOB_TYPE_CHOICES , blank=True)
    industry = models.ForeignKey(Industry , on_delete=models.SET_NULL , null=True , blank=True)
    min_salary = models.DecimalField(max_digits=10 , decimal_places=2 , null=True , blank=True)
    frequency = models.CharField(max_length=1 , choices=FREQUENCY_CHOICES , default='W')
    is_active = models.BooleanField(default=True)
    last_sent = models.DateTimeField(null=True , blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.keywords}"


class SavedJob(models.Model):
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    job = models.ForeignKey(Job , on_delete=models.CASCADE)
    saved_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('user' , 'job')
        ordering = ['-saved_date']


# Continuing models.py...

class Interview(models.Model):
    INTERVIEW_TYPE_CHOICES = [
        ('PH', 'Phone'),
        ('VI', 'Video'),
        ('F2F', 'Face to Face'),
        ('TS', 'Technical Screen'),
        ('AS', 'Assignment')
    ]

    STATUS_CHOICES = [
        ('SC', 'Scheduled'),
        ('IP', 'In Progress'),
        ('CM', 'Completed'),
        ('CN', 'Cancelled'),
        ('RS', 'Rescheduled')
    ]

    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='interviews')
    interview_type = models.CharField(max_length=3, choices=INTERVIEW_TYPE_CHOICES)
    scheduled_date = models.DateTimeField()
    duration = models.DurationField()
    location = models.CharField(max_length=200, blank=True)
    meeting_link = models.URLField(blank=True)
    interviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='conducted_interviews')
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='SC')
    feedback = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['scheduled_date']

    def __str__(self):
        return f"{self.get_interview_type_display()} Interview - {self.application.job.title}"

class Assessment(models.Model):
    TYPE_CHOICES = [
        ('SK', 'Skills Test'),
        ('PS', 'Problem Solving'),
        ('PG', 'Programming'),
        ('LG', 'Language'),
        ('PS', 'Personality'),
        ('CT', 'Custom')
    ]

    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='assessments')
    title = models.CharField(max_length=200)
    assessment_type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    description = models.TextField()
    instructions = models.TextField()
    duration = models.DurationField(null=True, blank=True)
    deadline = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.application.job.title}"

class Notification(models.Model):
    TYPE_CHOICES = [
        ('AP', 'Application Update'),
        ('IV', 'Interview Schedule'),
        ('JB', 'New Job Match'),
        ('MS', 'Message'),
        ('AS', 'Assessment'),
        ('SY', 'System')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.title}"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200)
    content = models.TextField()
    related_job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender.get_full_name()} to {self.receiver.get_full_name()} - {self.subject}"

class JobSeekerPreference(models.Model):
    job_seeker = models.OneToOneField(JobSeeker, on_delete=models.CASCADE, related_name='preferences')
    preferred_job_types = models.CharField(max_length=100, blank=True)
    preferred_locations = models.CharField(max_length=200, blank=True)
    preferred_industries = models.ManyToManyField(Industry, blank=True)
    min_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_open_to_remote = models.BooleanField(default=True)
    is_willing_to_relocate = models.BooleanField(default=False)
    notice_period = models.IntegerField(help_text="Notice period in days", null=True, blank=True)
    job_search_status = models.CharField(max_length=20, choices=[
        ('active', 'Actively Looking'),
        ('passive', 'Passively Looking'),
        ('not_looking', 'Not Looking')
    ], default='active')

    def __str__(self):
        return f"Preferences for {self.job_seeker.user.get_full_name()}"

class CompanyFollower(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='followers')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followed_companies')
    followed_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('company', 'user')

    def __str__(self):
        return f"{self.user.get_full_name()} follows {self.company.company_name}"