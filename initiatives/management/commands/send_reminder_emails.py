from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import date, timedelta, datetime
import logging
from initiatives.models import BrainstormingSession
from users.models import Member

logger = logging.getLogger(__name__)

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import date, timedelta, datetime
from initiatives.models import BrainstormingSession, Member
import logging
from django.utils.html import strip_tags
import html


# logger = logging.getLogger(__name__)
# class Command(BaseCommand):
#     help = 'Send reminder emails for tomorrow\'s brainstorming sessions'
#     def handle(self, *args, **kwargs):
#         logger.info("Task started: send_reminder_emails")
#         try:
#             # Get tomorrow's date
#             tomorrow = timezone.localtime(timezone.now()).date() + timedelta(days=1)
            
#             # Get tomorrow's sessions
#             sessions = BrainstormingSession.objects.filter(date=tomorrow).select_related('initiative', 'facilitator')
            
#             if not sessions.exists():
#                 message = f"No sessions scheduled for {tomorrow}"
#                 logger.info(message)
#                 self.stdout.write(message)
#                 return

#             # Get active members with emails
#             recipient_emails = list(
#                 Member.objects.filter(
#                     status='ACTIVE',
#                     user__email__isnull=False
#                 ).values_list('user__email', flat=True)
#                 .distinct()
#             )

#             if not recipient_emails:
#                 message = "No active members found with valid email addresses."
#                 logger.info(message)
#                 self.stdout.write(message)
#                 return

#             for session in sessions:
#                 subject = f"Reminder: {session.session_type} Brainstorming Session Tomorrow"
                
#                 message = f"""
#                     Dear Member,

#                     This is a reminder about tomorrow's brainstorming session:

#                     Session Type: {session.get_session_type_display()}
#                     Initiative: {session.initiative.name if hasattr(session.initiative, 'name') else 'N/A'}
#                     Date: {tomorrow.strftime('%A, %B %d, %Y')}
#                     Location: {session.location}
#                     Facilitator: {session.facilitator.user.get_full_name() if hasattr(session.facilitator.user, 'get_full_name') else session.facilitator}

#                     Agenda:
#                     {session.agenda}

#                     Please make sure to attend and come prepared for the discussion.

#                     Best regards,
#                     Your Team
#                                     """
#                 batch_size = 50
#                 for i in range(0, len(recipient_emails), batch_size):
#                     batch = recipient_emails[i:i + batch_size]
#                     try:
#                         send_mail(
#                             subject,
#                             message,
#                             settings.DEFAULT_FROM_EMAIL,
#                             batch,
#                             fail_silently=False,
#                         )
#                         logger.info(f"Sent emails to batch {i//batch_size + 1}")
#                     except Exception as e:
#                         logger.error(f"Failed to send email batch: {e}")
#                         self.stderr.write(f"Failed to send email batch: {e}")

#             self.stdout.write(
#                 self.style.SUCCESS(
#                     f"Successfully sent {len(sessions)} session reminder(s) to {len(recipient_emails)} members"
#                 )
#             )

#         except Exception as e:
#             error_message = f"Error sending reminder emails: {str(e)}"
#             logger.error(error_message)
#             self.stderr.write(self.style.ERROR(error_message))
#             raise

class Command(BaseCommand):
    help = 'Send reminder emails for tomorrow\'s brainstorming sessions'
    def clean_html_content(self, content):
        """Clean HTML content for email"""
        if content:
            # Decode HTML entities and strip HTML tags
            cleaned = html.unescape(strip_tags(content))
            # Remove extra whitespace
            cleaned = ' '.join(cleaned.split())
            return cleaned
        return ''
    def handle(self, *args, **kwargs):
        logger.info("Task started: send_reminder_emails")
        try:
            tomorrow = timezone.localtime(timezone.now()).date() + timedelta(days=1)
            sessions = BrainstormingSession.objects.filter(date=tomorrow).select_related('initiative', 'facilitator')
            if not sessions.exists():
                message = f"No sessions scheduled for {tomorrow}"
                logger.info(message)
                self.stdout.write(message)
                return
            recipient_emails = list(
                Member.objects.filter(
                    status='ACTIVE',
                    user__email__isnull=False
                ).values_list('user__email', flat=True)
                .distinct()
            )
            if not recipient_emails:
                message = "No active members found with valid email addresses."
                logger.info(message)
                self.stdout.write(message)
                return
            for session in sessions:
                facilitator_name = (
                    session.facilitator.user.get_full_name() 
                    if hasattr(session.facilitator, 'user') and session.facilitator.user.get_full_name() 
                    else str(session.facilitator)
                )
                # Clean the agenda content
                cleaned_agenda = self.clean_html_content(session.agenda)
                subject = f"Reminder: {session.get_session_type_display()} Session Tomorrow"
                message = f"""Dear Member,
                    This is a reminder about tomorrow's brainstorming session.
                    SESSION DETAILS
                    --------------
                    Type: {session.get_session_type_display()}
                    Initiative: {session.initiative.name if hasattr(session.initiative, 'name') else str(session.initiative)}
                    Date: {tomorrow.strftime('%A, %B %d, %Y')}
                    Location: {session.location}
                    Facilitator: {facilitator_name}
                    AGENDA
                    ------
                    {cleaned_agenda}
                    ADDITIONAL INFORMATION
                    ---------------------
                    • Expected participants: {session.participants_count}
                    • Please arrive 5 minutes early
                    • Bring any necessary materials
                    Please make sure to attend and come prepared for the discussion.
                    Best regards,
                    Gazra Team"""
                try:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        recipient_emails,
                        fail_silently=False,
                    )
                    logger.info(f"Successfully sent email for session {session.id}")
                except Exception as e:
                    logger.error(f"Failed to send email: {e}")
                    self.stderr.write(f"Failed to send email: {e}")
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