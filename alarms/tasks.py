from celery import shared_task
from django.conf import settings
from django.utils import timezone
from notifications.providers import get_notification_service
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_whatsapp_notification(alarm_id):
    """
    Send a WhatsApp notification for a new alarm using the configured notification provider.
    """
    from subjects.models import Alarm
    
    try:
        alarm = Alarm.objects.get(id=alarm_id)
        if alarm.notification_sent:
            logger.info(f"Notification already sent for alarm {alarm_id}")
            return
            
        # Get the notification service based on configuration
        notification_service = get_notification_service()
        
        # Get the custodian's phone number
        phone_number = alarm.subject.custodian.phone_number
        
        # Send the notification
        response = notification_service.send_message(
            to_number=phone_number,
            message=f"Alarm triggered for subject {alarm.subject.name} at {alarm.timestamp}"
        )
        
        # Check if the message was sent successfully
        if hasattr(response, 'status_code'):  # WhatsApp API response
            if response.status_code == 200:
                alarm.notification_sent = True
                alarm.save()
                logger.info(f"WhatsApp notification sent successfully for alarm {alarm_id}")
            else:
                logger.error(f"Failed to send WhatsApp notification for alarm {alarm_id}. Status code: {response.status_code}")
        else:  # Twilio response
            if response.sid:
                alarm.notification_sent = True
                alarm.save()
                logger.info(f"Twilio notification sent successfully for alarm {alarm_id}")
            else:
                logger.error(f"Failed to send Twilio notification for alarm {alarm_id}")
                
    except Alarm.DoesNotExist:
        logger.error(f"Alarm {alarm_id} not found")
    except Exception as e:
        logger.error(f"Error sending notification for alarm {alarm_id}: {str(e)}")

@shared_task
def retry_failed_notifications():
    """
    Retry sending notifications for alarms where notification failed.
    """
    from subjects.models import Alarm
    
    # Get alarms where notification wasn't sent
    failed_alarms = Alarm.objects.filter(
        notification_sent=False,
        timestamp__gte=timezone.now() - timezone.timedelta(days=1)  # Only last 24 hours
    )
    
    for alarm in failed_alarms:
        send_whatsapp_notification.delay(alarm.id)
        logger.info(f"Retrying notification for alarm {alarm.id}")

@shared_task
def cleanup_old_alarms():
    """
    Archive or delete old alarms (older than 30 days)
    """
    from .models import Alarm
    
    cutoff_date = timezone.now() - timezone.timedelta(days=30)
    old_alarms = Alarm.objects.filter(timestamp__lt=cutoff_date)
    
    # Here you might want to archive them instead of deleting
    count = old_alarms.count()
    old_alarms.delete()
    
    logger.info(f"Cleaned up {count} old alarms") 