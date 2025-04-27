from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
import atexit
import os
import logging
logger = logging.getLogger(__name__)

class TripsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'trips'

    def ready(self):
        if os.environ.get('RUN_MAIN'):
            logger.debug("AppConfig.ready() called")  # Debug line

            if os.environ.get('RUN_MAIN') or not os.environ.get('DJANGO_RUNSERVER'):
                logger.debug("Initializing scheduler")

                try:
                    scheduler = BackgroundScheduler()
                    scheduler.add_job(
                        self.run_daily_reminders,
                        'cron',
                        hour=8,
                        minute=0,
                        timezone='America/New_York'
                    )
                    scheduler.start()
                    logger.info("Scheduler started successfully")
                    atexit.register(lambda: scheduler.shutdown())
                except Exception as e:
                    logger.error(f"Failed to start scheduler: {e}")

        from . import signals

    def run_daily_reminders(self):
        from .tasks import task_creation
        from django_apscheduler.models import DjangoJobExecution
        from datetime import timedelta
        from django.utils import timezone
        # Import your function
        task_creation()  # Execute it

        DjangoJobExecution.objects.delete_old_job_executions(max_age=timedelta(days=7))