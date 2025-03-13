from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Alarm
from alarms.tasks import send_whatsapp_notification

@receiver(post_save, sender=Alarm)
def trigger_whatsapp_notification(sender, instance, created, **kwargs):
    """
    Trigger WhatsApp notification when a new alarm is created.
    """
    if created:
        send_whatsapp_notification.delay(instance.id) 