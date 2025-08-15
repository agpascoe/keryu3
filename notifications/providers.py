from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)

class WhatsAppAPIProvider:
    """WhatsApp Business API notification provider."""
    
    def __init__(self):
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.api_version = 'v18.0'
        self.base_url = f'https://graph.facebook.com/{self.api_version}/{self.phone_number_id}'
        
        # Log configuration
        logger.info(f'WhatsApp API Configuration:')
        logger.info(f'Phone Number ID: {self.phone_number_id}')
        logger.info(f'Access Token length: {len(self.access_token) if self.access_token else 0}')
        logger.info(f'Base URL: {self.base_url}')
    
    def validate_phone_number(self, phone_number):
        """Validate and clean phone number."""
        if not phone_number:
            raise ValueError("Phone number is required")
        
        # Clean the phone number (remove spaces and '+' symbol)
        cleaned = str(phone_number).replace(' ', '').replace('+', '')
        if not cleaned.isdigit():
            raise ValueError(f"Invalid phone number format: {phone_number}")
        
        return cleaned
    
    def parse_response(self, response):
        """Parse WhatsApp API response and extract relevant information."""
        try:
            data = response.json()
            
            # Check for error response
            if 'error' in data:
                return {
                    'success': False,
                    'error': data['error'].get('message', 'Unknown error'),
                    'code': data['error'].get('code', 'unknown'),
                    'status': 'ERROR'
                }
            
            # Extract message info
            if 'messages' in data and len(data['messages']) > 0:
                message = data['messages'][0]
                return {
                    'success': True,
                    'message_id': message.get('id'),
                    'status': message.get('message_status', 'SENT').upper(),
                    'recipient': data.get('contacts', [{}])[0].get('wa_id')
                }
            
            return {
                'success': False,
                'error': 'No message data in response',
                'status': 'ERROR'
            }
            
        except Exception as e:
            logger.error(f"Error parsing WhatsApp response: {str(e)}")
            return {
                'success': False,
                'error': f"Failed to parse response: {str(e)}",
                'status': 'ERROR'
            }
    
    def send_message(self, to_number, message_data):
        """Send a WhatsApp message using the Meta WhatsApp Business API."""
        try:
            # Validate phone number
            to_number = self.validate_phone_number(to_number)
            logger.info(f'Preparing to send message to: {to_number}')
            logger.info(f'Message data: {message_data}')
            
            if not message_data.get('subject_name') or not message_data.get('timestamp'):
                raise ValueError("Missing required message data: subject_name or timestamp")
            
            # Prepare the message payload using the template
            payload = {
                'messaging_product': 'whatsapp',
                'to': to_number,
                'type': 'template',
                'template': {
                    'name': 'qr_template_on_m',
                    'language': {
                        'code': 'en_US'
                    },
                    'components': [
                        {
                            'type': 'body',
                            'parameters': [
                                {
                                    'type': 'text',
                                    'text': message_data['subject_name']
                                },
                                {
                                    'type': 'text',
                                    'text': message_data['timestamp']
                                }
                            ]
                        }
                    ]
                }
            }
            
            # Set up headers with authentication
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Log the request details
            logger.info('Sending request to WhatsApp API:')
            logger.info(f'URL: {self.base_url}/messages')
            logger.info(f'Headers: {headers}')
            logger.info(f'Payload: {payload}')
            
            # Send the request to WhatsApp API
            response = requests.post(
                f'{self.base_url}/messages',
                json=payload,
                headers=headers
            )
            
            # Log the response
            logger.info(f'WhatsApp API Response Status: {response.status_code}')
            logger.info(f'WhatsApp API Response Headers: {dict(response.headers)}')
            logger.info(f'WhatsApp API Response Body: {response.text}')
            
            # Parse and return the response
            result = self.parse_response(response)
            result['status_code'] = response.status_code
            return result
            
        except ValueError as ve:
            logger.error(f'Validation error: {str(ve)}')
            return {
                'success': False,
                'error': str(ve),
                'status': 'ERROR',
                'status_code': 400
            }
        except requests.RequestException as e:
            logger.error(f'Network error sending WhatsApp message: {str(e)}')
            return {
                'success': False,
                'error': f'Network error: {str(e)}',
                'status': 'ERROR',
                'status_code': getattr(e.response, 'status_code', 500)
            }
        except Exception as e:
            logger.error(f'Unexpected error sending WhatsApp message: {str(e)}')
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'status': 'ERROR',
                'status_code': 500
            }

def get_notification_service():
    """Get the configured notification service based on the channel setting."""
    from django.conf import settings
    
    # Check if we're in development mode
    if hasattr(settings, 'NOTIFICATION_PROVIDER') and settings.NOTIFICATION_PROVIDER == 'console':
        from .console_provider import get_console_notification_service
        return get_console_notification_service()
    
    # Production providers
    try:
        from core.models import SystemParameter
        from core.messaging import MessageChannel
        
        channel_param = SystemParameter.objects.get(parameter='channel')
        channel = MessageChannel(channel_param.value)
        
        if channel == MessageChannel.TWILIO_SMS:
            from twilio.rest import Client
            client = Client(
                username=settings.TWILIO_ACCOUNT_SID,
                password=settings.TWILIO_AUTH_TOKEN,
                account_sid=settings.TWILIO_ACCOUNT_SID
            )
            return client
        else:
            return WhatsAppAPIProvider()
    except (SystemParameter.DoesNotExist, ImportError):
        # Default to WhatsApp if no channel is configured
        return WhatsAppAPIProvider() 