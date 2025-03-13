from django.conf import settings

# Notification provider configuration
NOTIFICATION_PROVIDER = getattr(settings, 'NOTIFICATION_PROVIDER', 'whatsapp_api')  # Options: 'whatsapp_api' or 'twilio'

# WhatsApp API Configuration
WHATSAPP_API_CONFIG = {
    'phone_number_id': getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', ''),
    'access_token': getattr(settings, 'WHATSAPP_ACCESS_TOKEN', ''),
    'template_name': 'hello_world',  # Default template name
}

# Twilio Configuration
TWILIO_CONFIG = {
    'account_sid': getattr(settings, 'TWILIO_ACCOUNT_SID', ''),
    'auth_token': getattr(settings, 'TWILIO_AUTH_TOKEN', ''),
    'from_number': getattr(settings, 'TWILIO_FROM_NUMBER', ''),
    'whatsapp_sandbox': getattr(settings, 'TWILIO_WHATSAPP_SANDBOX', True),  # True for sandbox, False for production
}

def get_notification_provider():
    """
    Returns the current notification provider name.
    """
    provider = getattr(settings, 'NOTIFICATION_PROVIDER', 'whatsapp_api')
    if provider not in ['whatsapp_api', 'twilio']:
        raise ValueError(f"Unsupported notification provider: {provider}")
    return provider 