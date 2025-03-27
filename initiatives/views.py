from django.shortcuts import render

# Create your views here.
from datetime import timedelta, date
from django.utils.timezone import now
from django.core.mail import send_mass_mail
from .models import BrainstormingSession
from users.models import Member
from celery import shared_task

# @shared_task
# def send_reminder_emails():
#     tomorrow = date.today() + timedelta(days=1)
#     sessions = BrainstormingSession.objects.filter(date=tomorrow)
#     if not sessions.exists():
#         return "No sessions scheduled for tomorrow."
#     recipient_emails = list(
#         Member.objects.filter(status='ACTIVE').values_list('user__email', flat=True)
#     )
#     if not recipient_emails:
#         return "No active members found with email addresses."
#     email_data = []
#     for session in sessions:
#         subject = f"Reminder: {session.get_session_type_display()} Session Tomorrow"
#         message = (
#             f"Dear Member,\n\n"
#             f"We'd like to remind you of the upcoming brainstorming session:\n\n"
#             f"Session Type: {session.get_session_type_display()}\n"
#             f"Initiative: {session.initiative.name}\n"
#             f"Date: {session.date}\n"
#             f"Location: {session.location}\n"
#             f"Facilitator: {session.facilitator.user.first_name} {session.facilitator.user.last_name}\n\n"
#             f"Agenda: {session.agenda}\n\n"
#             f"We look forward to your participation!\n\n"
#             f"Best Regards,\n"
#             f"The Team"
#         )
#         email_data.append((subject, message, 'support@gazra.org', recipient_emails))
#     send_mass_mail(email_data)
#     return f"Emails successfully sent to {len(recipient_emails)} members."



from django.http import JsonResponse
from celery.result import AsyncResult

def check_task_status(request, task_id):
    result = AsyncResult(task_id)  
    if result.ready():
        return JsonResponse({'status': 'completed', 'result': result.result})
    else:
        return JsonResponse({'status': 'processing', 'message': 'Task is still processing...'})


# views.py

from django.http import JsonResponse
# from initiatives.tasks import long_task

# def start_long_task(request):
#     long_task.delay()  # Calling the Celery task
#     return JsonResponse({"status": "Task started"})
