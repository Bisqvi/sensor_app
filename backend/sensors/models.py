# backend/sensors/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    pass

class Sensor(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sensors')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    model = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.model})"

    class Meta:
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['name']),
            models.Index(fields=['model']),
        ]

class Reading(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='readings')
    temperature = models.FloatField()
    humidity = models.FloatField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.sensor.name} reading at {self.timestamp}"

    class Meta:
        indexes = [
            models.Index(fields=['sensor', 'timestamp']),
        ]

