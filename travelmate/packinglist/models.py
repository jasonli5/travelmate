from django.db import models
from django.contrib.auth.models import User
from trips.models import inputTrip


class Item(models.Model):
    trip = models.ForeignKey(inputTrip, on_delete=models.CASCADE, related_name='items', null=True, blank=True)
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_ai_suggested = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id) + " - " + self.name
