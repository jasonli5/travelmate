from background_task import background, Task
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
        if trip.created_at >= timezone.now - timedelta(3) and trip.end_date < timezone.now:
            recipients.append(trip.user, trip.destination)
    return recipients

#background task syntax, added params for message and trip
@background(schedule=60)
def notify_user(user_id, message):
    user = User.objects.get(pk=user_id)
    user.email_user("TravelMate Reminder: Complete your Trip", message)

remind_users = get_recipients() #creating list of tuples

#calling notify_user for each user to be reminded about specified old trip
for (user, trip) in remind_users:
    msg = render_to_string("reminder.html",{'user': user, 'trip': trip})
    notify_user(user.id, msg, repeat=Task.DAILY, repeat_until=date(2025,5,2))
