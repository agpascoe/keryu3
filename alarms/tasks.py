from celery import shared_task
from django.conf import settings
from django.utils import timezone
import requests
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_whatsapp_notification(self, alarm_id):
    """
    Send WhatsApp notification for an alarm.
    """
    from .models import Alarm  # Import here to avoid circular imports
    
    try:
        alarm = Alarm.objects.select_related(
            'subject__custodian'
        ).get(id=alarm_id)
        
        # Prepare the API request
        url = f"https://graph.facebook.com/v22.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }
        data = {
            "messaging_product": "whatsapp",
            "to": str(alarm.subject.custodian.phone_number).replace("+", ""),  # Remove + prefix
            "type": "template",
            "template": {
                "name": "hello_world",
                "language": {
                    "code": "en_US"
                }
            }
        }
        
        # Send the WhatsApp message
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            # Update alarm status
            alarm.notification_sent = True
            alarm.notification_sent_at = timezone.now()
            alarm.save()
            logger.info(f"WhatsApp notification sent successfully for alarm {alarm_id}")
            return True
            
        else:
            logger.error(
                f"Failed to send WhatsApp notification for alarm {alarm_id}. "
                f"Status code: {response.status_code}, Response: {response.text}"
            )
            raise Exception(f"WhatsApp API returned status code {response.status_code}")
            
    except Alarm.DoesNotExist:
        logger.error(f"Alarm {alarm_id} not found")
        return False
        
    except requests.RequestException as e:
        logger.error(f"Network error while sending WhatsApp notification: {str(e)}")
        raise self.retry(exc=e, countdown=60)  # Retry after 1 minute
        
    except Exception as e:
        logger.error(f"Error sending WhatsApp notification: {str(e)}")
        raise self.retry(exc=e, countdown=300)  # Retry after 5 minutes

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