# tasks.py in one of your Django apps

from celery import shared_task
from datetime import date, datetime, timedelta
from django.utils.timezone import now
from django.core.mail import send_mass_mail
from .models import BrainstormingSession
from users.models import Member
import logging
from django.core.mail import send_mail
from django.conf import settings
import pytz
from time import sleep
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

# @shared_task
# def add(x, y):
#     return x + y

# @shared_task
# def debug_task():
#     print("Celery Task Executed!")

# @shared_task
# def long_task():
#     print("Starting long task...")
#     sleep(10)  
#     print("Long task completed!")
#     return "Task finished successfully!"

# @shared_task
# def send_reminder_emails():
#     logger.info("Task started: send_reminder_emails")
#     try:
#         tomorrow = date.today() + timedelta(days=1)
#         logger.info(f"Checking for sessions on {tomorrow}")
#         sessions = BrainstormingSession.objects.filter(date=tomorrow)
#         logger.info(f"Found {sessions.count()} sessions for tomorrow")
#         if not sessions.exists():
#             logger.info("No sessions scheduled for tomorrow.")
#             return "No sessions scheduled for tomorrow."
#         recipient_emails = list(
#             Member.objects.filter(status='ACTIVE').values_list('user__email', flat=True)
#         )
#         logger.info(f"Found {len(recipient_emails)} active members")
#         if not recipient_emails:
#             logger.info("No active members found with email addresses.")
#             return "No active members found with email addresses."  
#         logger.info(f"Email host: {settings.EMAIL_HOST}")
#         logger.info(f"Email port: {settings.EMAIL_PORT}")
#         logger.info(f"Email user: {settings.EMAIL_HOST_USER}")
#         email_data = []
#         for session in sessions:
#             subject = f"Reminder: Brainstorming Session Tomorrow"
#             message = (
#                 f"Dear Member,\n\n"
#                 f"Test email for session {session.id}\n"
#             )
#             try:
#                 from django.core.mail import send_mail
#                 send_mail(
#                     subject,
#                     message,
#                     settings.EMAIL_HOST_USER,
#                     recipient_emails,
#                     fail_silently=False,
#                 )
#                 logger.info(f"Test email sent successfully for session {session.id}")
#             except Exception as email_error:
#                 logger.error(f"Email error: {str(email_error)}")
#                 raise  
#         success_message = f"Emails successfully sent to {len(recipient_emails)} members."
#         logger.info(success_message)
#         return success_message
#     except Exception as e:
#         error_message = f"Error occurred while sending reminder emails: {str(e)}"
#         logger.error(error_message, exc_info=True)
#         raise 


from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Send reminder emails for tomorrow\'s brainstorming sessions'

    def handle(self, *args, **kwargs):
        logger.info("Task started: send_reminder_emails")
        try:
            # Get tomorrow's date in the correct timezone
            tomorrow = timezone.localtime(timezone.now()).date() + timedelta(days=1)
            
            # Get tomorrow's sessions
            sessions = BrainstormingSession.objects.filter(date=tomorrow)
            
            if not sessions.exists():
                message = f"No sessions scheduled for {tomorrow}"
                logger.info(message)
                self.stdout.write(message)
                return

            # Get active members with emails
            recipient_emails = list(
                Member.objects.filter(
                    status='ACTIVE',
                    user__email__isnull=False  # Ensure email exists
                ).values_list('user__email', flat=True)
                .distinct()  # Avoid duplicate emails
            )

            if not recipient_emails:
                message = "No active members found with valid email addresses."
                logger.info(message)
                self.stdout.write(message)
                return

            for session in sessions:
                # Format time properly
                session_time = session.time.strftime("%I:%M %p") if isinstance(session.time, datetime) else session.time
                
                subject = f"Reminder: Brainstorming Session Tomorrow - {session.title}"
                message = f"""
                            Dear Member,

                            This is a reminder about tomorrow's brainstorming session:

                            Session: {session.title}
                            Date: {tomorrow.strftime('%A, %B %d, %Y')}
                            Time: {session_time}

                            Please make sure to attend and come prepared for the discussion.

                            Best regards,
                            Your Team
                                            """

                # Send email in smaller batches to avoid timeouts
                batch_size = 50
                for i in range(0, len(recipient_emails), batch_size):
                    batch = recipient_emails[i:i + batch_size]
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        batch,
                        fail_silently=False,
                    )
                    logger.info(f"Sent emails to batch {i//batch_size + 1}")

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully sent {len(sessions)} session reminder(s) to {len(recipient_emails)} members"
                )
            )

        except Exception as e:
            error_message = f"Error sending reminder emails: {str(e)}"
            logger.error(error_message)
            self.stderr.write(self.style.ERROR(error_message))
            raise


from django.core.mail import send_mail
from django_q.tasks import async_task

# Define the task
def send_email_task(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        'support@gazra.org',  # sender's email
        recipient_list,
        fail_silently=False,
    )

# Optionally, you can create a task for scheduling:
def schedule_email_task(subject, message, recipient_list):
    async_task('initiatives.tasks.send_email_task', subject, message, recipient_list)

# myapp/tasks.py

from django_q.tasks import async_task

def simple_task():
    print("Task executed!")
    return "Task executed successfully!"

# Call the task asynchronously
async_task('initiatives.tasks.simple_task')

from django_q.tasks import async_task
async_task('initiatives.tasks.my_task')

from django_q.tasks import async_task

def my_test_task():
    return "Task completed successfully"
# Push a test task to the queue
async_task(my_test_task)
