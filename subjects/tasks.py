from celery import shared_task
from django.conf import settings
import requests
import logging
from .models import Alarm
from notifications.providers import get_notification_service

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_whatsapp_notification(self, alarm_id):
    """
    Send WhatsApp notification for an alarm using the WhatsApp Business API.
    """
    try:
        alarm = Alarm.objects.get(id=alarm_id)
        subject = alarm.subject
        custodian = subject.custodian
        
        # Skip if notification was already sent
        if alarm.notification_sent:
            logger.info(f"Notification already sent for alarm {alarm_id}")
            return
        
        # Prepare the message data for the template
        message_data = {
            'subject_name': subject.name,
            'timestamp': alarm.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Get the WhatsApp API service
        notification_service = get_notification_service()
        logger.info(f"Sending notification to: {custodian.phone_number}")
        
        # Send the notification
        response = notification_service.send_message(
            to_number=custodian.phone_number,
            message_data=message_data
        )
        
        # Handle the WhatsApp API response
        if response.status_code == 200:
            alarm.notification_sent = True
            alarm.save()
            logger.info(f"WhatsApp notification sent successfully for alarm {alarm_id}")
        else:
            error_msg = f"Failed to send WhatsApp notification. Status: {response.status_code}, Response: {response.text}"
            logger.error(error_msg)
            alarm.notification_error = error_msg
            alarm.save()
            raise self.retry(exc=Exception(error_msg), countdown=60)
        
    except Alarm.DoesNotExist:
        logger.error(f"Alarm {alarm_id} not found")
    except requests.exceptions.RequestException as e:
        error_msg = f"API request failed: {str(e)}"
        logger.error(error_msg)
        alarm.notification_error = error_msg
        alarm.save()
        raise self.retry(exc=e, countdown=60)
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        if 'alarm' in locals():
            alarm.notification_error = error_msg
            alarm.save()
        raise self.retry(exc=e, countdown=60) 