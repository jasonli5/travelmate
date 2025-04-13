from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class inputTrip(models.Model):
    user = models.ForeignKey(User,null=True, on_delete=models.CASCADE)
    destination = models.CharField("Chosen Destination", max_length=200)
    start_date = models.DateField("Start Date")
    end_date = models.DateField("End Date")
    activities = models.TextField("Desired Activities", max_length=500)
