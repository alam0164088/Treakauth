from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('vendor', 'Vendor'),
        ('traveler', 'Traveler'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="traveler")
    receive_notifications = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
