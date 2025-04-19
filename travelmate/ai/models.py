from django.db import models
from trips.models import inputTrip

class Activity(models.Model):
    """
    Model representing an activity.
    """
    name = models.CharField(max_length=255)
    trip = models.ForeignKey(inputTrip, on_delete=models.CASCADE, related_name='activities')

    def __str__(self):
        return self.name