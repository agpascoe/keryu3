from celery import shared_task
from django.conf import settings
import requests
import logging
from .models import Alarm

logger = logging.getLogger(__name__)

@shared_task
def send_whatsapp_notification(alarm_id):
    """
    Send WhatsApp notification for an alarm using the Meta WhatsApp Business API.
    """
    try:
        alarm = Alarm.objects.get(id=alarm_id)
        subject = alarm.subject
        custodian = subject.custodian
        
        # Prepare the message
        message = (
            f"🚨 ALERT: {subject.name} has triggered an alarm!\n\n"
            f"Location: {alarm.location or 'Unknown'}\n"
            f"Time: {alarm.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"Please check on {subject.name} immediately."
        )
        
        # Prepare the API request
        url = f"https://graph.facebook.com/v17.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }
        data = {
            "messaging_product": "whatsapp",
            "to": str(custodian.phone_number),
            "type": "text",
            "text": {"body": message}
        }
        
        # Send the request
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        # Update alarm status
        alarm.notification_sent = True
        alarm.save()
        
        logger.info(f"Successfully sent WhatsApp notification for alarm {alarm_id}")
        
    except Alarm.DoesNotExist:
        logger.error(f"Alarm {alarm_id} not found")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send WhatsApp notification for alarm {alarm_id}: {str(e)}")
        alarm.notification_error = str(e)
        alarm.save()
    except Exception as e:
        logger.error(f"Unexpected error sending WhatsApp notification for alarm {alarm_id}: {str(e)}")
        alarm.notification_error = str(e)
        alarm.save() 