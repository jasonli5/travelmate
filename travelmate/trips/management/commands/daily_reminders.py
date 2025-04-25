from django.core.management.base import BaseCommand
from trips.tasks import task_creation  # Import your function

class Command(BaseCommand):
    help = 'Creates daily reminder tasks'

    def handle(self, *args, **options):
        task_creation()  # Calls your task_creation() function
        self.stdout.write("Daily reminders created")