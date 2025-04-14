from django.db import models

class Destination(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name}, {self.country}"

class Activity(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='activities')

    def __str__(self):
        return f"{self.name} - {self.destination.name}"
