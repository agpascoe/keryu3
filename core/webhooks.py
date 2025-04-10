from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from alarms.models import Alarm, NotificationStatus
import logging
from django.db import transaction

logger = logging.getLogger(__name__)

TWILIO_STATUS_MAP = {
    'QUEUED': NotificationStatus.PENDING,
    'SENDING': NotificationStatus.PROCESSING,
    'SENT': NotificationStatus.SENT,
    'DELIVERED': NotificationStatus.DELIVERED,
    'UNDELIVERED': NotificationStatus.FAILED,
    'FAILED': NotificationStatus.ERROR
}

@csrf_exempt
@require_POST
def twilio_status_callback(request):
    """Handle Twilio message status callback"""
    message_sid = request.POST.get('MessageSid')
    message_status = request.POST.get('MessageStatus')
    error_code = request.POST.get('ErrorCode')
    error_message = request.POST.get('ErrorMessage')
    
    logger.info(f"Received Twilio webhook - MessageSid: {message_sid}, Status: {message_status}")
    
    if not message_sid:
        logger.error("No MessageSid in Twilio callback")
        return HttpResponse(status=400)
        
    try:
        # Use transaction.atomic with select_for_update to prevent race conditions
        with transaction.atomic():
            # Get alarm with lock to prevent concurrent updates
            alarm = Alarm.objects.select_for_update().get(message_sid=message_sid)
            
            # Log current status
            logger.info(f"Current alarm status: {alarm.notification_status}")
            
            # Map Twilio status to our status - convert to uppercase first
            new_status = TWILIO_STATUS_MAP.get(message_status.upper(), NotificationStatus.ERROR)
            
            # Only update if status is different
            if alarm.notification_status != new_status:
                logger.info(f"Updating alarm {alarm.id} status from {alarm.notification_status} to {new_status}")
                alarm.notification_status = new_status
                
                # Set notification_sent based on status
                if new_status in [NotificationStatus.SENT, NotificationStatus.DELIVERED]:
                    alarm.notification_sent = True
                elif new_status in [NotificationStatus.FAILED, NotificationStatus.ERROR]:
                    alarm.notification_sent = False
                
                # Save error details if present
                if error_code or error_message:
                    error_details = f"Code: {error_code}, Message: {error_message}"
                    alarm.notification_error = error_details
                    alarm.save(update_fields=['notification_status', 'notification_sent', 'notification_error'])
                else:
                    alarm.save(update_fields=['notification_status', 'notification_sent'])
            else:
                logger.info(f"Alarm {alarm.id} status already set to {new_status}, skipping update")
            
    except Alarm.DoesNotExist:
        logger.error(f"No alarm found for message_sid {message_sid}")
    except Exception as e:
        logger.error(f"Error processing Twilio callback: {str(e)}")
        
    return HttpResponse(status=200) 