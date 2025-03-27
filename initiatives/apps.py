from django.apps import AppConfig


class InitiativesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'initiatives'

    def ready(self):
        try:
            from .scheduler import setup_email_reminder_schedule
            setup_email_reminder_schedule()
        except Exception as e:
            print(f"Failed to set up scheduler: {e}")
