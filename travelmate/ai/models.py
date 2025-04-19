from django.db import models
from trips.models import inputTrip

class Activity(models.Model):
    """
    Model representing an activity.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    trip = models.ForeignKey(inputTrip, on_delete=models.CASCADE, related_name='activities')
    is_ai_suggested = models.BooleanField(default=False)

    def __str__(self):
        return self.name