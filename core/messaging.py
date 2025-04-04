import os
from enum import Enum
from twilio.rest import Client
from django.conf import settings
from .models import SystemParameter
from notifications.providers import get_notification_service
import logging

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
        if account_sid and auth_token:
            # Initialize client with explicit basic auth
            self.twilio_client = Client(
                username=account_sid,
                password=auth_token,
                account_sid=account_sid
            )
    
    def _send_twilio_whatsapp(self, to_number: str, message: str) -> dict:
        """Send WhatsApp message using Twilio"""
        if not self.twilio_client:
            return {"status": "error", "error": "Twilio client not initialized"}
        
        try:
            formatted_number = format_phone_number(to_number, MessageChannel.TWILIO_WHATSAPP)
            wa_to = f"whatsapp:{formatted_number}"
            wa_from = f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}"
            
            # Format message to match Meta API style
            formatted_message = format_message(message)
            
            message = self.twilio_client.messages.create(
                body=formatted_message,
                from_=wa_from,
                to=wa_to
            )
            
            return {
                "status": "success",
                "message_sid": message.sid,
                "to": message.to,
                "from": message.from_,
                "body": message.body,
                "channel": "twilio_whatsapp"
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "channel": "twilio_whatsapp"}
    
    def _send_twilio_sms(self, to_number: str, message: str) -> dict:
        """Send SMS using Twilio"""
        if not self.twilio_client:
            return {"status": "error", "error": "Twilio client not initialized"}
        
        try:
            # Send message directly without extra formatting
            message = self.twilio_client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to_number
            )
            
            return {
                "status": "success",
                "message_sid": message.sid,
                "to": message.to,
                "from": message.from_,
                "body": message.body,
                "channel": "twilio_sms"
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "channel": "twilio_sms"}
    
    def _send_meta_whatsapp(self, to_number: str, message: str) -> dict:
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
            
            result = self.whatsapp_provider.send_message(formatted_number, message_data)
            
            return {
                "status": "success" if result.get('success') else "error",
                "to": to_number,
                "body": formatted_message,
                "channel": "meta_whatsapp",
                "meta_result": result
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "channel": "meta_whatsapp"}
    
    def send_message(self, to_number: str, message: str) -> dict:
        """
        Send message using the configured channel from SystemParameter
        """
        try:
            # Get the configured channel from SystemParameter
            channel_param = SystemParameter.objects.get(parameter='notification_channel')
            channel = MessageChannel(channel_param.value)
            
            # Format message
            formatted_message = format_message(message)
            
            # Send message using the appropriate channel
            if channel == MessageChannel.TWILIO_SMS:
                return self._send_twilio_sms(to_number, formatted_message)
            elif channel == MessageChannel.TWILIO_WHATSAPP:
                return self._send_twilio_whatsapp(to_number, formatted_message)
            elif channel == MessageChannel.META_WHATSAPP:
                return self._send_meta_whatsapp(to_number, formatted_message)
            else:
                return {"status": "error", "error": f"Unsupported channel: {channel}"}
                
        except SystemParameter.DoesNotExist:
            # Default to Twilio SMS if no channel is configured
            logger.warning("No notification channel configured, defaulting to Twilio SMS")
            return self._send_twilio_sms(to_number, message)
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return {"status": "error", "error": str(e)} 