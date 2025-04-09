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
from .models import Alarm, NotificationStatus

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
            if alarm.notification_status == NotificationStatus.SENT:
                logger.info(f"Notification for alarm {alarm_id} already sent")
                return True
            elif alarm.notification_status == NotificationStatus.PROCESSING:
                logger.info(f"Notification for alarm {alarm_id} is already in progress")
                return True
            
            # Check if enough time has passed since last attempt (minimum 2 minutes)
            if alarm.last_attempt and (timezone.now() - alarm.last_attempt).total_seconds() < 120:
                logger.info(f"Not enough time has passed since last attempt for alarm {alarm_id}")
                return True
            
            # Mark as in progress
            alarm.notification_status = NotificationStatus.PROCESSING
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
                    message=message,
                    alarm=alarm  # Pass the alarm object
                )
                
                # Update alarm status based on response
                if result.get('status') == 'success' or (isinstance(result.get('meta_result'), dict) and result['meta_result'].get('success')):
                    # First mark as accepted by the service
                    alarm.notification_status = NotificationStatus.ACCEPTED
                    alarm.notification_sent = True
                    alarm.last_attempt = timezone.now()
                    alarm.notification_attempt_count += 1
                    alarm.notification_error = None
                    
                    # Store message ID based on channel
                    if result.get('message_id'):
                        alarm.message_sid = result['message_id']
                    elif isinstance(result.get('meta_result'), dict) and result['meta_result'].get('message_id'):
                        alarm.whatsapp_message_id = result['meta_result']['message_id']
                    
                    alarm.save(update_fields=[
                        'notification_status',
                        'notification_sent',
                        'last_attempt',
                        'notification_attempt_count',
                        'notification_error',
                        'message_sid',
                        'whatsapp_message_id'
                    ])
                    
                    logger.info(f"Successfully queued notification for alarm {alarm_id}")
                    return True
                else:
                    error_msg = result.get('error') or (result.get('meta_result', {}) or {}).get('error', 'Unknown error')
                    raise Exception(f"Failed to send message: {error_msg}")
                
            except Exception as e:
                # Handle notification failure
                alarm.notification_status = NotificationStatus.FAILED
                alarm.notification_attempt_count += 1
                alarm.notification_error = str(e)
                alarm.save(update_fields=[
                    'notification_status',
                    'notification_attempt_count',
                    'notification_error'
                ])
                
                logger.error(f"Failed to send notification for alarm {alarm_id}: {str(e)}")
                
                # Retry with exponential backoff if under max retries
                if alarm.notification_attempt_count < 3:
                    # Calculate retry delay: minimum 2 minutes, maximum 10 minutes
                    retry_delay = min(max(120, 2 ** self.request.retries * 60), 600)
                    raise self.retry(exc=e, countdown=retry_delay)
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
    # Get alarms where notification wasn't sent or failed
    failed_alarms = Alarm.objects.filter(
        Q(notification_sent=False) | Q(notification_status__in=[NotificationStatus.ERROR, NotificationStatus.FAILED]),
        notification_attempt_count__lt=3,  # Limit retries to 3 attempts
        timestamp__gte=timezone.now() - timezone.timedelta(days=1)  # Only last 24 hours
    )
    
    for alarm in failed_alarms:
        send_whatsapp_notification.delay(alarm.id)
        logger.info(f"Retrying notification for alarm {alarm.id} (Attempt {alarm.notification_attempt_count + 1})")

@shared_task(bind=True, max_retries=3)
def process_pending_alarms(self):
    """
    Process all pending alarms and send notifications
    """
    logger.info("Starting to process pending alarms...")
    
    # Get all pending alarms that haven't been attempted in the last 2 minutes
    two_minutes_ago = timezone.now() - timezone.timedelta(minutes=2)
    pending_alarms = Alarm.objects.filter(
        notification_status=NotificationStatus.PENDING,
        notification_attempt_count__lt=3
    ).exclude(
        last_attempt__gt=two_minutes_ago
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
            with transaction.atomic():
                # Get alarm with lock to prevent race conditions
                alarm = Alarm.objects.select_for_update(nowait=True).get(id=alarm.id)
                
                logger.info(f"Processing alarm {alarm.id} for subject {alarm.subject.name}")
                
                # Skip if already sent or in progress
                if alarm.notification_status == NotificationStatus.SENT:
                    logger.info(f"Notification for alarm {alarm.id} already sent")
                    continue
                elif alarm.notification_status == NotificationStatus.PROCESSING:
                    logger.info(f"Notification for alarm {alarm.id} is already in progress")
                    continue
                
                # Check if enough time has passed since last attempt
                if alarm.last_attempt and (timezone.now() - alarm.last_attempt).total_seconds() < 120:
                    logger.info(f"Not enough time has passed since last attempt for alarm {alarm.id}")
                    continue
                
                # Mark as in progress
                alarm.notification_status = NotificationStatus.PROCESSING
                alarm.save(update_fields=['notification_status'])
                
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
                
                logger.info(f"Sending notification to {phone_str} for alarm {alarm.id}")
                
                # Send notification using configured channel
                result = message_service.send_message(
                    to_number=phone_str,
                    message=message,
                    alarm=alarm  # Pass the alarm object
                )
                
                # Update alarm status based on response
                if result.get('status') == 'success' or (isinstance(result.get('meta_result'), dict) and result['meta_result'].get('success')):
                    alarm.notification_status = NotificationStatus.SENT
                    alarm.notification_sent = True
                    alarm.last_attempt = timezone.now()
                    alarm.notification_attempt_count += 1
                    alarm.notification_error = None
                    
                    # Store message ID based on channel
                    if result.get('message_id'):
                        alarm.message_sid = result['message_id']
                    elif isinstance(result.get('meta_result'), dict) and result['meta_result'].get('message_id'):
                        alarm.whatsapp_message_id = result['meta_result']['message_id']
                    
                    alarm.save(update_fields=[
                        'notification_status',
                        'notification_sent',
                        'last_attempt',
                        'notification_attempt_count',
                        'notification_error',
                        'message_sid',
                        'whatsapp_message_id'
                    ])
                    processed_count += 1
                    logger.info(f"Successfully sent notification for alarm {alarm.id}")
                else:
                    error_msg = result.get('error') or (result.get('meta_result', {}) or {}).get('error', 'Unknown error')
                    raise Exception(f"Failed to send message: {error_msg}")
                
        except Exception as e:
            error_count += 1
            logger.error(f"Error processing alarm {alarm.id}: {str(e)}")
            try:
                alarm.notification_status = NotificationStatus.ERROR
                alarm.notification_error = str(e)
                alarm.notification_attempt_count += 1
                alarm.save(update_fields=['notification_status', 'notification_error', 'notification_attempt_count'])
            except Exception as save_error:
                logger.error(f"Error saving alarm status: {str(save_error)}")
    
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