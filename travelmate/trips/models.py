from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.

class inputTrip(models.Model):
    created_at = models.DateTimeField(default= timezone.now)
    user = models.ForeignKey(User,null=True, on_delete=models.CASCADE)
    destination = models.CharField("Chosen Destination", max_length=200)
    start_date = models.DateField("Start Date")
    end_date = models.DateField("End Date")
    activities = models.TextField("Desired Activities", max_length=500)

    def __str__(self):
        return f"{self.destination} ({self.start_date} to {self.end_date}) - #{self.id}"

    class Meta:
        ordering = ['created_at']  # Optional: orders trips by start date (newest first)
        verbose_name = "Trip"  # Optional: nicer name in admin
        verbose_name_plural = "Trips"  # Optional

class travelRecommendations(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='travel_recs/')

    def __str__(self):
        return self.name

