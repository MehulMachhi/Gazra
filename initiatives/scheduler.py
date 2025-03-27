from django_q.tasks import schedule
from django_q.models import Schedule

# def setup_email_reminder_schedule():
#     # Schedule the task to run daily at 10:30 AM
#     schedule(
#         'python manage.py send_reminder_emails',
#         schedule_type='C',  # Cron-style schedule
#         cron='30 14 * * *',  # Run at 10:30 AM daily
#         queue='default'
#     )

def setup_email_reminder_schedule():
    # Delete any existing schedules with this name to avoid duplicates
    Schedule.objects.filter(name='daily_reminder_emails').delete()
    schedule(
        'django.core.management.call_command',  
        'send_reminder_emails',                 
        schedule_type='C',
        cron='00 15 * * *',  
        name='daily_reminder_emails',
        repeats=-1
    )