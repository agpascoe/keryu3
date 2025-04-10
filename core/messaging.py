import os
from enum import Enum
from twilio.rest import Client
from django.conf import settings
from .models import SystemParameter
from notifications.providers import get_notification_service
import logging
from twilio.base.exceptions import TwilioRestException
from alarms.models import Alarm, NotificationStatus
from django.utils import timezone
from django.db import transaction

logger = logging.getLogger(__name__)

class MessageChannel(Enum):
    META_WHATSAPP = "1"  # Default Meta WhatsApp API
    TWILIO_WHATSAPP = "2"  # Twilio WhatsApp
    TWILIO_SMS = "3"  # Twilio SMS

def format_phone_number(phone_number: str, channel: MessageChannel) -> str:
    """
    Format phone number according to the channel requirements.
    """
    # Remove any existing prefixes or formatting
    clean_number = phone_number.replace("whatsapp:", "").strip()
    return clean_number

def format_message(message: str) -> str:
    """
    Format message to ensure consistency across all channels.
    This follows the Meta API message format.
    """
    # Remove any extra whitespace and normalize line endings
    formatted_message = " ".join(message.split())
    return formatted_message

class MessageService:
    def __init__(self):
        self.twilio_client = None
        self.whatsapp_provider = get_notification_service()
        self._initialize_twilio()
    
    def _initialize_twilio(self):
        """Initialize Twilio client if credentials are available"""
        account_sid = settings.TWILIO_ACCOUNT_SID
        auth_token = settings.TWILIO_AUTH_TOKEN
        
        if not account_sid or not auth_token:
            logger.error("Twilio credentials not configured")
            return
            
        try:
            # Initialize client using standard method
            self.twilio_client = Client(account_sid, auth_token)
            logger.info("Twilio client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Twilio client: {str(e)}")
            self.twilio_client = None
    
    def _send_twilio_whatsapp(self, to_number: str, message: str, alarm: Alarm = None) -> dict:
        """Send WhatsApp message using Twilio"""
        if not self.twilio_client:
            error_msg = "Twilio client not initialized"
            if alarm:
                alarm.notification_status = NotificationStatus.ERROR
                alarm.notification_error = error_msg
                alarm.notification_attempt_count += 1
                alarm.last_attempt = timezone.now()
                alarm.save(update_fields=[
                    'notification_status',
                    'notification_error',
                    'notification_attempt_count',
                    'last_attempt'
                ])
            return {"status": "error", "error": error_msg, "channel": "twilio_whatsapp"}
        
        try:
            formatted_number = format_phone_number(to_number, MessageChannel.TWILIO_WHATSAPP)
            wa_to = f"whatsapp:{formatted_number}"
            wa_from = f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}"
            
            # Format message to match Meta API style
            formatted_message = format_message(message)
            
            message = self.twilio_client.messages.create(
                body=formatted_message,
                from_=wa_from,
                to=wa_to,
                status_callback=settings.TWILIO_STATUS_CALLBACK_URL
            )
            
            # Update alarm status if provided
            if alarm:
                alarm.notification_status = NotificationStatus.PROCESSING
                alarm.message_sid = message.sid
                alarm.last_attempt = timezone.now()
                alarm.notification_attempt_count += 1
                alarm.notification_error = None
                alarm.save(update_fields=[
                    'notification_status',
                    'message_sid',
                    'last_attempt',
                    'notification_attempt_count',
                    'notification_error'
                ])
            
            return {
                "status": "success",
                "message_sid": message.sid,
                "to": message.to,
                "from": message.from_,
                "body": message.body,
                "channel": "twilio_whatsapp"
            }
        except Exception as e:
            error_msg = str(e)
            if alarm:
                alarm.notification_status = NotificationStatus.ERROR
                alarm.notification_error = error_msg
                alarm.notification_attempt_count += 1
                alarm.last_attempt = timezone.now()
                alarm.save(update_fields=[
                    'notification_status',
                    'notification_error',
                    'notification_attempt_count',
                    'last_attempt'
                ])
            return {"status": "error", "error": error_msg, "channel": "twilio_whatsapp"}
    
    def _send_twilio_sms(self, to_number: str, message: str, alarm: Alarm = None) -> dict:
        """
        Send SMS message using Twilio
        """
        if not self.twilio_client:
            error_msg = "Twilio client not initialized"
            logger.error(error_msg)
            if alarm:
                alarm.notification_status = NotificationStatus.ERROR
                alarm.notification_error = error_msg
                alarm.notification_attempt_count += 1
                alarm.last_attempt = timezone.now()
                alarm.save(update_fields=[
                    'notification_status',
                    'notification_error',
                    'notification_attempt_count',
                    'last_attempt'
                ])
            return {"status": "error", "error": error_msg, "channel": "twilio_sms"}
            
        try:
            # Log the attempt
            logger.info(f"Attempting to send SMS to {to_number}")
            
            # Send message using Twilio client
            message = self.twilio_client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to_number,
                status_callback=settings.TWILIO_STATUS_CALLBACK_URL
            )
            
            # Log success
            logger.info(f"Successfully queued SMS. Message SID: {message.sid}")
            
            # Update alarm status if provided
            if alarm:
                # Use transaction to ensure atomic update
                with transaction.atomic():
                    # Get alarm with lock to prevent race conditions
                    alarm = Alarm.objects.select_for_update().get(id=alarm.id)
                    
                    # Set initial status to PENDING (will be updated by webhook)
                    alarm.notification_status = NotificationStatus.PENDING
                    alarm.message_sid = message.sid
                    alarm.last_attempt = timezone.now()
                    alarm.notification_attempt_count += 1
                    alarm.notification_error = None
                    alarm.save(update_fields=[
                        'notification_status',
                        'message_sid',
                        'last_attempt',
                        'notification_attempt_count',
                        'notification_error'
                    ])
                
                logger.info(f"Updated alarm {alarm.id} with message_sid {message.sid} and status {NotificationStatus.PENDING}")
            
            return {
                "status": "success",
                "message_id": message.sid,
                "channel": "twilio_sms"
            }
            
        except TwilioRestException as e:
            error_msg = f"Twilio SMS error: {str(e)}"
            logger.error(error_msg)
            
            # Update alarm status to error if provided
            if alarm:
                alarm.notification_status = NotificationStatus.ERROR
                alarm.notification_error = error_msg
                alarm.notification_attempt_count += 1
                alarm.last_attempt = timezone.now()
                alarm.save(update_fields=[
                    'notification_status',
                    'notification_error',
                    'notification_attempt_count',
                    'last_attempt'
                ])
                
            return {
                "status": "error",
                "error": error_msg,
                "channel": "twilio_sms"
            }
    
    def _send_meta_whatsapp(self, to_number: str, message: str, alarm: Alarm = None) -> dict:
        """
        Send WhatsApp message using Meta API.
        This method uses the WhatsAppAPIProvider implementation.
        """
        try:
            # Format message to match Meta API style
            formatted_message = format_message(message)
            
            # Format phone number (remove '+' for Meta API)
            formatted_number = to_number.replace("+", "")
            
            # Prepare message data for the template
            message_data = {
                'subject_name': formatted_message,
                'timestamp': 'now'  # You might want to pass this as a parameter
            }
            
            # Update alarm status to processing before sending
            if alarm:
                alarm.notification_status = NotificationStatus.PROCESSING
                alarm.last_attempt = timezone.now()
                alarm.notification_attempt_count += 1
                alarm.notification_error = None
                alarm.save(update_fields=[
                    'notification_status',
                    'last_attempt',
                    'notification_attempt_count',
                    'notification_error'
                ])
            
            result = self.whatsapp_provider.send_message(formatted_number, message_data)
            
            # Update alarm with message ID if successful
            if alarm and result.get('success'):
                alarm.whatsapp_message_id = result.get('message_id')
                alarm.save(update_fields=['whatsapp_message_id'])
            elif alarm:
                alarm.notification_status = NotificationStatus.ERROR
                alarm.notification_error = result.get('error', 'Unknown error')
                alarm.save(update_fields=['notification_status', 'notification_error'])
            
            return {
                "status": "success" if result.get('success') else "error",
                "to": to_number,
                "body": formatted_message,
                "channel": "meta_whatsapp",
                "meta_result": result
            }
        except Exception as e:
            error_msg = str(e)
            if alarm:
                alarm.notification_status = NotificationStatus.ERROR
                alarm.notification_error = error_msg
                alarm.notification_attempt_count += 1
                alarm.last_attempt = timezone.now()
                alarm.save(update_fields=[
                    'notification_status',
                    'notification_error',
                    'notification_attempt_count',
                    'last_attempt'
                ])
            return {"status": "error", "error": error_msg, "channel": "meta_whatsapp"}
    
    def send_message(self, to_number: str, message: str, alarm: Alarm = None) -> dict:
        """
        Send message using the configured channel from SystemParameter
        """
        try:
            # Get the configured channel from SystemParameter
            channel_param = SystemParameter.objects.get(parameter='channel')
            channel = MessageChannel(channel_param.value)
            
            # Format message
            formatted_message = format_message(message)
            
            # Send message using the appropriate channel
            if channel == MessageChannel.TWILIO_SMS:
                return self._send_twilio_sms(to_number, formatted_message, alarm)
            elif channel == MessageChannel.TWILIO_WHATSAPP:
                return self._send_twilio_whatsapp(to_number, formatted_message, alarm)
            elif channel == MessageChannel.META_WHATSAPP:
                return self._send_meta_whatsapp(to_number, formatted_message, alarm)
            else:
                return {"status": "error", "error": f"Unsupported channel: {channel}"}
                
        except SystemParameter.DoesNotExist:
            # Default to Twilio SMS if no channel is configured
            logger.warning("No notification channel configured, defaulting to Twilio SMS")
            return self._send_twilio_sms(to_number, message, alarm)
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return {"status": "error", "error": str(e)} 