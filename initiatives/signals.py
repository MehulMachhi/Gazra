from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BrainstormingSession
from .tasks import send_reminder_emails
from datetime import timedelta, datetime

# @receiver(post_save, sender=BrainstormingSession)
# def schedule_reminder_email(sender, instance, created, **kwargs):
#     """
#     This signal will schedule the sending of reminder emails one day before the session date.
#     """
#     if created:  # Ensure the task runs only when a new session is created
#         # Calculate the date for sending the reminder email (1 day before session date)
#         reminder_date = instance.date - timedelta(days=1)
        
#         # Set the exact time for when the email should be sent (9:00 AM on reminder_date)
#         eta_time = datetime.combine(reminder_date, datetime.min.time()) + timedelta(hours=9)  # 9 AM

#         # Schedule the email sending task at the exact `eta_time`
#         send_reminder_emails.apply_async(
#             eta=eta_time,  # Set the exact time when the email should be sent
#             kwargs={'session_id': instance.id}
#         )

from datetime import datetime
import pytz
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .tasks import send_reminder_emails
from django.utils.timezone import localtime
logger = logging.getLogger(__name__)

# @receiver(post_save, sender=BrainstormingSession)
# def schedule_reminder_email(sender, instance, created, **kwargs):
#     if created:  
#         reminder_time = instance.date.replace(hour=13, minute=28, second=0, microsecond=0)
#         local_timezone = pytz.timezone('Asia/Kolkata')
#         reminder_time_local = localtime(reminder_time, local_timezone)
#         reminder_time_local = datetime.now(local_timezone) + timedelta(minutes=1)
#         logger.info(f'Scheduling reminder email for session {instance.id} at {reminder_time_local}')
#         send_reminder_emails.apply_async(
#             eta=reminder_time_local, 
#             kwargs={'session_id': instance.id}
#         )