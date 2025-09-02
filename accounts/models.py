from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

# User Model
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

# Password Reset OTP
class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)

# Notification
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.message[:20]}"

# Vendor
class Vendor(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vendor")
    location_lat = models.FloatField()
    location_lng = models.FloatField()

    def __str__(self):
        return self.name

# Reward
class Reward(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="rewards")
    name = models.CharField(max_length=100)
    description = models.TextField()
    visits_required = models.IntegerField(default=1)
    max_redemptions_per_day = models.IntegerField(default=10)
    qr_code = models.ImageField(upload_to="rewards_qr/", blank=True, null=True)
    valid_until = models.DateTimeField()

    def __str__(self):
        return f"{self.name} ({self.vendor.name})"

# CheckIn
class CheckIn(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    entry_time = models.DateTimeField()
    exit_time = models.DateTimeField(null=True, blank=True)

# RewardRedemption
class RewardRedemption(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    redeemed_at = models.DateTimeField(auto_now_add=True)
    qr_validated = models.BooleanField(default=False)

# Signal: Automatically create Vendor when a new User with role='vendor' is created
@receiver(post_save, sender=User)
def create_vendor_for_user(sender, instance, created, **kwargs):
    if created and instance.role == "vendor":
        Vendor.objects.create(
            name=f"{instance.username}'s Vendor",
            owner=instance,
            location_lat=0.0,
            location_lng=0.0
        )