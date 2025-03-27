from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
from datetime import date, datetime, timedelta
from .models import BrainstormingSession
from users.models import Member
from django.core.mail import send_mail
from django.conf import settings

def myCron(self, *args, **kwargs):
        logger.info("Task started: send_reminder_emails")
        try:
            tomorrow = date.today() + timedelta(days=1)
            sessions = BrainstormingSession.objects.filter(date=tomorrow)
            if not sessions.exists():
                self.stdout.write("No sessions scheduled for tomorrow.")
                return

            recipient_emails = list(
                Member.objects.filter(status='ACTIVE').values_list('user__email', flat=True)
            )
            if not recipient_emails:
                self.stdout.write("No active members found with email addresses.")
                return

            for session in sessions:
                subject = f"Reminder: Brainstorming Session Tomorrow"
                message = (
                    f"Dear Member,\n\n"
                    f"This is a reminder about tomorrow's brainstorming session:\n"
                    f"Session: {session.title}\n"
                    f"Date: {session.date}\n"
                    f"Time: {session.time}\n\n"
                    f"Best regards,\n"
                    f"Your Team"
                )
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    recipient_emails,
                    fail_silently=False,
                )
            self.stdout.write(f"Emails successfully sent to {len(recipient_emails)} members.")

        except Exception as e:
            logger.error(f"Error: {e}")
            self.stderr.write(f"Error occurred: {str(e)}")
