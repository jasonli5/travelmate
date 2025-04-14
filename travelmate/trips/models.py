from django.db import models

from django.contrib.auth.models import User

class Trip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="trips")
    destination = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.destination} ({self.start_date} to {self.end_date})"
