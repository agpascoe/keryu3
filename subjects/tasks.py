from celery import shared_task
from django.conf import settings
import requests
import logging
from .models import Alarm

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_whatsapp_notification(self, alarm_id):
    """
    Send WhatsApp notification for an alarm using WhatsApp Business API.
    Retries up to 3 times with exponential backoff if sending fails.
    """
    try:
        alarm = Alarm.objects.select_related('subject__custodian').get(id=alarm_id)
        
        # Prepare message
        message = (
            f"⚠️ *ALERT*: {alarm.subject.name} needs attention!\n\n"
            f"📅 Time: {alarm.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        
        if alarm.location:
            lat, lng = alarm.location.split(',')
            message += f"📍 Location: https://maps.google.com/?q={lat},{lng}\n"
        
        # WhatsApp API endpoint
        url = f"https://graph.facebook.com/v17.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }
        
        # Prepare payload
        payload = {
            "messaging_product": "whatsapp",
            "to": alarm.subject.custodian.phone,
            "type": "text",
            "text": {"body": message}
        }
        
        # Send request
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        # Update alarm status
        alarm.notification_sent = True
        alarm.notification_error = None
        alarm.save()
        
        logger.info(f"WhatsApp notification sent successfully for alarm {alarm_id}")
        
    except Alarm.DoesNotExist:
        logger.error(f"Alarm {alarm_id} not found")
        return
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send WhatsApp notification for alarm {alarm_id}: {str(e)}")
        alarm.notification_error = str(e)
        alarm.save()
        
        # Retry with exponential backoff
        retry_in = 2 ** self.request.retries * 60  # 1min, 2min, 4min
        raise self.retry(exc=e, countdown=retry_in)
        
    except Exception as e:
        logger.error(f"Unexpected error sending WhatsApp notification for alarm {alarm_id}: {str(e)}")
        alarm.notification_error = str(e)
        alarm.save() 