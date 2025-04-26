import json

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.

class inputTrip(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    destination = models.CharField("Chosen Destination", max_length=200)
    start_date = models.DateField("Start Date")
    end_date = models.DateField("End Date")
    collaborators = models.ManyToManyField(User, blank=True, related_name='collaborative_trips')


    # ✅ Add these new editable fields:
    weather = models.TextField("Weather Info", blank=True, null=True)
    packing_list = models.TextField("Packing List", blank=True, null=True)

    activities_list = models.TextField("Activities List", blank=True, null=True)

    considerations = models.JSONField("Additional Considerations", blank=True, null=True)

    def __str__(self):
        return f"{self.destination}: [{self.user}] - ({self.start_date} to {self.end_date}) - #{self.id}"

    class Meta:
        ordering = ['created_at']
        verbose_name = "Trip"
        verbose_name_plural = "Trips"


class travelRecommendations(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='travel_recs/')
    def __str__(self):
        return self.name

class TripInvite(models.Model):
    trip = models.ForeignKey(inputTrip, on_delete=models.CASCADE)
    email = models.EmailField()
    invited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} invited to {self.trip.destination}"


