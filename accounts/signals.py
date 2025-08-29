from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import User

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:  # নতুন ইউজার হলে
        subject = "Welcome to TrekBot!"
        message = f"Hi {instance.username}, welcome to TrekBot! Enjoy your journey."
        recipient_list = [instance.email]
        
        send_mail(
            subject,
            message,
            None,  # from_email will use DEFAULT_FROM_EMAIL
            recipient_list,
            fail_silently=False,
        )
