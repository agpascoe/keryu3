from celery import shared_task
from django.conf import settings
from django.utils import timezone
from notifications.providers import get_notification_service
import logging
from django.db.models import Q

logger = logging.getLogger(__name__)

@shared_task
def send_whatsapp_notification(alarm_id):
    """
    Send a WhatsApp notification for a new alarm using the configured notification provider.
    """
    from subjects.models import Alarm
    
    try:
        alarm = Alarm.objects.get(id=alarm_id)
        
        # Don't retry if notification was already sent successfully
        if alarm.notification_sent and alarm.notification_status in ['SENT', 'DELIVERED']:
            logger.info(f"Notification already sent successfully for alarm {alarm_id}")
            return
            
        # Get the notification service based on configuration
        notification_service = get_notification_service()
        
        # Get the custodian's phone number
        phone_number = alarm.subject.custodian.phone_number
        if not phone_number:
            raise ValueError(f"No phone number found for custodian of subject {alarm.subject.name}")
        
        # Increment attempt counter and update timestamp
        alarm.notification_attempts += 1
        alarm.last_attempt = timezone.now()
        alarm.save()
        
        # Send the notification
        response = notification_service.send_message(
            to_number=phone_number,
            message_data={
                'subject_name': alarm.subject.name,
                'timestamp': alarm.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }
        )
        
        # Process the response
        if response['success']:
            alarm.notification_sent = True
            alarm.notification_status = response['status']
            alarm.whatsapp_message_id = response.get('message_id')
            alarm.notification_error = None
            logger.info(f"WhatsApp notification sent successfully for alarm {alarm_id}")
        else:
            alarm.notification_sent = False
            alarm.notification_status = response['status']
            alarm.notification_error = f"Error: {response.get('error', 'Unknown error')}"
            logger.error(f"Failed to send WhatsApp notification for alarm {alarm_id}. Error: {response.get('error')}")
        
        alarm.save()
                
    except Alarm.DoesNotExist:
        logger.error(f"Alarm {alarm_id} not found")
    except ValueError as ve:
        logger.error(f"Validation error for alarm {alarm_id}: {str(ve)}")
        try:
            alarm = Alarm.objects.get(id=alarm_id)
            alarm.notification_status = 'ERROR'
            alarm.notification_error = str(ve)
            alarm.save()
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Error sending notification for alarm {alarm_id}: {str(e)}")
        try:
            alarm = Alarm.objects.get(id=alarm_id)
            alarm.notification_status = 'ERROR'
            alarm.notification_error = str(e)
            alarm.save()
        except Exception:
            pass

@shared_task
def retry_failed_notifications():
    """
    Retry sending notifications for alarms where notification failed.
    """
    from subjects.models import Alarm
    
    # Get alarms where notification wasn't sent or failed
    failed_alarms = Alarm.objects.filter(
        Q(notification_sent=False) | Q(notification_status__in=['ERROR', 'FAILED']),
        notification_attempts__lt=3,  # Limit retries to 3 attempts
        timestamp__gte=timezone.now() - timezone.timedelta(days=1)  # Only last 24 hours
    )
    
    for alarm in failed_alarms:
        send_whatsapp_notification.delay(alarm.id)
        logger.info(f"Retrying notification for alarm {alarm.id} (Attempt {alarm.notification_attempts + 1})")

@shared_task
def cleanup_old_alarms():
    """
    Archive or delete old alarms (older than 30 days)
    """
    from subjects.models import Alarm
    
    cutoff_date = timezone.now() - timezone.timedelta(days=30)
    old_alarms = Alarm.objects.filter(timestamp__lt=cutoff_date)
    
    # Here you might want to archive them instead of deleting
    count = old_alarms.count()
    old_alarms.delete()
    
    logger.info(f"Cleaned up {count} old alarms") 