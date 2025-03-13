import requests
import logging
from twilio.rest import Client
from django.conf import settings
from core.notification_config import get_notification_provider

logger = logging.getLogger(__name__)

class WhatsAppAPIProvider:
    def __init__(self):
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.template_name = 'hello_world'
        self.api_url = f"https://graph.facebook.com/v22.0/{self.phone_number_id}/messages"

    def send_message(self, to_number, message):
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "messaging_product": "whatsapp",
            "to": to_number.lstrip('+'),
            "type": "template",
            "template": {
                "name": self.template_name,
                "language": {
                    "code": "en_US"
                }
            }
        }

        response = requests.post(self.api_url, headers=headers, json=data)
        return response

class TwilioProvider:
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.from_number = settings.TWILIO_FROM_NUMBER
        self.sandbox = settings.TWILIO_WHATSAPP_SANDBOX
        self.client = Client(self.account_sid, self.auth_token)
        logger.debug(f"Initialized TwilioProvider with sandbox={self.sandbox}, from_number={self.from_number}")

    def send_message(self, to_number, message):
        try:
            # Format the numbers according to Twilio's WhatsApp requirements
            if self.sandbox:
                # In sandbox mode, both numbers need the 'whatsapp:' prefix
                from_number = f"whatsapp:{self.from_number}"
                to_number = f"whatsapp:{to_number}"
            else:
                # In production, only the from_number needs the prefix
                from_number = f"whatsapp:{self.from_number}"

            logger.debug(f"Sending message to {to_number} from {from_number}")
            message = self.client.messages.create(
                body=message,
                from_=from_number,
                to=to_number
            )
            logger.info(f"Successfully sent message with SID: {message.sid}")
            return message
        except Exception as e:
            logger.error(f"Failed to send Twilio message: {str(e)}")
            raise

def get_notification_service():
    """
    Factory function to get the appropriate notification service based on configuration.
    """
    provider = getattr(settings, 'NOTIFICATION_PROVIDER', 'whatsapp_api')
    logger.debug(f"Using notification provider: {provider}")
    
    if provider == 'whatsapp_api':
        return WhatsAppAPIProvider()
    elif provider == 'twilio':
        return TwilioProvider()
    else:
        raise ValueError(f"Unsupported notification provider: {provider}") 