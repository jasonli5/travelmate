from background_task import background
from django.contrib.auth.models import User
from trips.models import inputTrip
from datetime import date, timedelta
from django.utils import timezone
from django.template.loader import render_to_string


#identifies users with trips more than 3 days old, returns list of tuples (user, old trip)
def get_recipients():
    trips = inputTrip.objects.all()
    recipients = []
    for trip in trips:
        if trip.notified is False and timezone.now().date() <= trip.start_date - timedelta(5):
            recipients.append((trip.user, trip))
    return recipients

#background task syntax, added params for message and trip
import logging
logger = logging.getLogger(__name__)

@background(schedule=60)
def notify_user(user_id, message):
    try:
        print("worked!")
        user = User.objects.get(pk=user_id)
        user.email_user("TravelMate Reminder: Complete your Trip", message)
    except Exception as e:
        print("failed!")
        logger.error(f"Failed to send email to user {user_id}: {e}")

# Test function to manually trigger task creation
def task_creation():
    remind_users = get_recipients()
    print(remind_users)
    for (user, trip) in remind_users:
        msg = render_to_string("reminder.html", {
            'user': user,
            'trip': trip,
            'trip_id': trip.id
        })
        notify_user(user.id, msg)
        trip.notified = True
    print(f"Created {len(remind_users)} tasks")



