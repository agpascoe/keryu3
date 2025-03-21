from celery import shared_task
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging
from django.db.models import Q
from core.messaging import MessageService
import requests
from notifications.providers import get_notification_service
from core.celery import app
from django.db import transaction
from .models import Alarm

logger = logging.getLogger(__name__)

@app.task(bind=True, max_retries=3, name='alarms.tasks.send_whatsapp_notification')
def send_whatsapp_notification(self, alarm_id, is_test=False):
    """
    Send a WhatsApp notification for an alarm.
    Uses select_for_update to prevent race conditions.
    """
    try:
        with transaction.atomic():
            # Get alarm with lock
            alarm = Alarm.objects.select_for_update(nowait=True).get(id=alarm_id)
            
            # Check if notification is already sent or in progress
            if alarm.notification_status == 'SENT':
                logger.info(f"Notification for alarm {alarm_id} already sent")
                return True
            elif alarm.notification_status == 'IN_PROGRESS':
                logger.info(f"Notification for alarm {alarm_id} is already in progress")
                return True
            
            # Mark as in progress
            alarm.notification_status = 'IN_PROGRESS'
            alarm.save(update_fields=['notification_status'])
            
            # Get notification service
            service = MessageService()
            
            try:
                # Prepare message with timestamp
                message = (
                    f"{'[TEST] ' if is_test else ''}"
                    f"Alert: {alarm.subject.name} has been located at "
                    f"{alarm.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                
                if alarm.location:
                    message += f"\nLocation: {alarm.location}"
                
                # Convert phone number to string format
                phone_str = str(alarm.subject.custodian.phone_number)
                if not phone_str.startswith('+'):
                    phone_str = f"+{phone_str}"
                
                # Attempt to send notification
                result = service.send_message(
                    to_number=phone_str,
                    message=message
                )
                
                # Update alarm status based on response
                if result['status'] == 'success':
                    alarm.notification_status = 'SENT'
                    alarm.notification_sent = True
                    alarm.last_attempt = timezone.now()
                    alarm.notification_attempts += 1
                    alarm.notification_error = None
                    alarm.save(update_fields=[
                        'notification_status',
                        'notification_sent',
                        'last_attempt',
                        'notification_attempts',
                        'notification_error'
                    ])
                    
                    logger.info(f"Successfully sent notification for alarm {alarm_id}")
                    return True
                else:
                    raise Exception(f"Failed to send message: {result.get('error', 'Unknown error')}")
                
            except Exception as e:
                # Handle notification failure
                alarm.notification_status = 'FAILED'
                alarm.notification_attempts += 1
                alarm.notification_error = str(e)
                alarm.save(update_fields=[
                    'notification_status',
                    'notification_attempts',
                    'notification_error'
                ])
                
                logger.error(f"Failed to send notification for alarm {alarm_id}: {str(e)}")
                
                # Retry with exponential backoff if under max retries
                if alarm.notification_attempts < 3:
                    raise self.retry(exc=e, countdown=2 ** self.request.retries)
                else:
                    logger.error(f"Max retries reached for alarm {alarm_id}")
                return False
                
    except Alarm.DoesNotExist:
        logger.error(f"Alarm {alarm_id} not found")
        return False
        
    except Exception as e:
        logger.error(f"Unexpected error processing alarm {alarm_id}: {str(e)}")
        raise

@shared_task
def retry_failed_notifications():
    """
    Retry sending notifications for alarms where notification failed.
    """
    from .models import Alarm
    
    # Get alarms where notification wasn't sent or failed
    failed_alarms = Alarm.objects.filter(
        Q(notification_sent=False) | Q(notification_status__in=['ERROR', 'FAILED']),
        notification_attempts__lt=3,  # Limit retries to 3 attempts
        timestamp__gte=timezone.now() - timezone.timedelta(days=1)  # Only last 24 hours
    )
    
    for alarm in failed_alarms:
        send_whatsapp_notification.delay(alarm.id)
        logger.info(f"Retrying notification for alarm {alarm.id} (Attempt {alarm.notification_attempts + 1})")

@shared_task(bind=True, max_retries=3)
def process_pending_alarms(self):
    """
    Process all pending alarms and send notifications
    """
    from .models import Alarm
    
    logger.info("Starting to process pending alarms...")
    
    # Get all pending alarms
    pending_alarms = Alarm.objects.filter(
        notification_status='PENDING',
        notification_attempts__lt=3
    )
    
    logger.info(f"Found {pending_alarms.count()} pending alarms to process")
    
    if not pending_alarms.exists():
        logger.info("No pending alarms to process")
        return
    
    message_service = MessageService()
    processed_count = 0
    error_count = 0
    
    for alarm in pending_alarms:
        try:
            logger.info(f"Processing alarm {alarm.id} for subject {alarm.subject.name}")
            
            # Get the custodian's phone number
            phone_number = alarm.subject.custodian.phone_number
            if not phone_number:
                raise ValueError(f"No phone number found for custodian of subject {alarm.subject.name}")
            
            # Convert phone number to string format
            phone_str = str(phone_number)
            if not phone_str.startswith('+'):
                phone_str = f"+{phone_str}"
            
            # Prepare the message
            message = f"Alert: {alarm.subject.name} has been located at {alarm.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Increment attempt counter and update timestamp
            alarm.notification_attempts += 1
            alarm.last_attempt = timezone.now()
            alarm.save()
            
            logger.info(f"Sending notification to {phone_str} for alarm {alarm.id}")
            
            # Send notification using configured channel
            response = message_service.send_message(
                to_number=phone_str,
                message=message
            )
            
            # Process the response
            if response['status'] == 'success':
                alarm.notification_status = 'SENT'
                alarm.notification_sent = True
                alarm.notification_error = None
                processed_count += 1
                logger.info(f"Notification sent successfully for alarm {alarm.id} via {response.get('channel', 'unknown')}")
            else:
                alarm.notification_status = 'ERROR'
                alarm.notification_error = f"Error: {response.get('error', 'Unknown error')}"
                error_count += 1
                logger.error(f"Failed to send notification for alarm {alarm.id}. Error: {response.get('error')}")
            
            alarm.save()
            
        except Exception as e:
            error_count += 1
            logger.error(f"Error processing alarm {alarm.id}: {str(e)}")
            try:
                alarm.notification_status = 'ERROR'
                alarm.notification_error = str(e)
                alarm.save()
            except Exception:
                pass
    
    logger.info(f"Finished processing alarms. Processed: {processed_count}, Errors: {error_count}")
    return {'processed': processed_count, 'errors': error_count}

@shared_task
def cleanup_old_alarms():
    """
    Archive or delete old alarms (older than 30 days)
    """
    from .models import Alarm
    
    cutoff_date = timezone.now() - timezone.timedelta(days=30)
    old_alarms = Alarm.objects.filter(timestamp__lt=cutoff_date)
    
    count = old_alarms.count()
    old_alarms.delete()
    
    logger.info(f"Cleaned up {count} old alarms") 