from django.db.models.signals import post_save
from django.dispatch import receiver
from alarms.models import Alarm
from alarms.tasks import send_whatsapp_notification
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Alarm)
def send_alarm_notification(sender, instance, created, **kwargs):
    """Send notification when a new alarm is created"""
    if created:  # Only for newly created alarms
        if instance.notification_status != 'SENT':  # Check if notification hasn't been sent
            if instance.is_test:
                # For test alarms, log and send with test flag
                logger.info(f"Sending test notification for alarm {instance.id}")
                send_whatsapp_notification.delay(instance.id, is_test=True)
            else:
                # For regular alarms
                logger.info(f"Sending notification for alarm {instance.id}")
                send_whatsapp_notification.delay(instance.id, is_test=False) 