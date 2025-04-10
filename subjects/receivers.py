from django.db.models.signals import post_save
from django.dispatch import receiver
from alarms.models import Alarm, NotificationStatus
from alarms.tasks import send_whatsapp_notification
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Alarm)
def send_alarm_notification(sender, instance, created, **kwargs):
    """Send notification when a new alarm is created"""
    if created:  # Only for newly created alarms
        logger.info(f"Signal handler triggered for new alarm {instance.id}")
        
        # Check if notification hasn't been sent and status is PENDING
        if instance.notification_status == NotificationStatus.PENDING:
            try:
                if instance.is_test:
                    # For test alarms, log and send with test flag
                    logger.info(f"Queueing test notification for alarm {instance.id}")
                    send_whatsapp_notification.delay(instance.id, is_test=True)
                else:
                    # For regular alarms
                    logger.info(f"Queueing notification for alarm {instance.id}")
                    send_whatsapp_notification.delay(instance.id, is_test=False)
            except Exception as e:
                logger.error(f"Error queueing notification for alarm {instance.id}: {str(e)}")
                # Update alarm status to ERROR
                instance.notification_status = NotificationStatus.ERROR
                instance.notification_error = str(e)
                instance.save(update_fields=['notification_status', 'notification_error'])
        else:
            logger.info(f"Alarm {instance.id} notification status is {instance.notification_status}, skipping notification") 