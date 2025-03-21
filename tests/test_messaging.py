import pytest
from unittest.mock import patch, MagicMock
from django.test import override_settings
from core.messaging import MessageService, MessageChannel, format_phone_number, format_message
from core.models import SystemParameter

TWILIO_TEST_SETTINGS = {
    'TWILIO_ACCOUNT_SID': 'test_account_sid',
    'TWILIO_AUTH_TOKEN': 'test_auth_token',
    'TWILIO_PHONE_NUMBER': '+1234567890',
    'TWILIO_WHATSAPP_NUMBER': '+1234567890'
}

@pytest.fixture
def mock_whatsapp_provider():
    mock_provider = MagicMock()
    mock_provider.send_message.return_value = {
        'messaging_product': 'whatsapp',
        'contacts': [{'wa_id': '1234567890'}],
        'messages': [{'id': 'wamid.test123'}]
    }
    return mock_provider

@pytest.fixture
def message_service(settings, mock_twilio_client, mock_whatsapp_provider):
    for key, value in TWILIO_TEST_SETTINGS.items():
        setattr(settings, key, value)
    with patch('core.messaging.get_notification_service', return_value=mock_whatsapp_provider):
        yield MessageService()

@pytest.fixture
def mock_twilio_client():
    with patch('core.messaging.Client') as mock_client:
        mock_client.return_value = MagicMock()
        mock_client.return_value.messages = MagicMock()
        mock_client.return_value.messages.create = MagicMock()
        yield mock_client

def test_format_phone_number():
    # Test Mexican number formatting for Twilio channels
    assert format_phone_number("+5212345678901", MessageChannel.TWILIO_WHATSAPP) == "+52112345678901"
    assert format_phone_number("+5212345678901", MessageChannel.TWILIO_SMS) == "+52112345678901"
    
    # Test Mexican number remains unchanged for Meta WhatsApp
    assert format_phone_number("+5212345678901", MessageChannel.META_WHATSAPP) == "+5212345678901"
    
    # Test non-Mexican numbers remain unchanged
    assert format_phone_number("+1234567890", MessageChannel.TWILIO_WHATSAPP) == "+1234567890"
    assert format_phone_number("+1234567890", MessageChannel.META_WHATSAPP) == "+1234567890"

def test_format_message():
    # Test whitespace normalization
    assert format_message("Hello   World\n\nTest") == "Hello World Test"
    assert format_message("Multiple    Spaces    Here") == "Multiple Spaces Here"
    assert format_message("No\nLine\nBreaks") == "No Line Breaks"

@pytest.mark.django_db
@override_settings(**TWILIO_TEST_SETTINGS)
def test_message_consistency_across_channels(message_service, mock_twilio_client, mock_whatsapp_provider):
    # Test message with extra whitespace and line breaks
    test_message = "Hello   World\nTest   Message\n\nWith Spaces"
    expected_formatted = "Hello World Test Message With Spaces"
    test_number = "+5212345678901"
    
    # Mock Twilio client responses
    mock_message = MagicMock()
    mock_message.sid = "test_sid"
    mock_message.to = test_number
    mock_message.body = expected_formatted
    mock_twilio_client.return_value.messages.create.return_value = mock_message
    
    # Test Meta WhatsApp channel
    SystemParameter.objects.get_or_create(parameter="channel", defaults={"value": MessageChannel.META_WHATSAPP.value})
    result = message_service.send_message(test_number, test_message)
    
    # Verify the message was formatted correctly
    mock_whatsapp_provider.send_message.assert_called_once()
    args, kwargs = mock_whatsapp_provider.send_message.call_args
    assert args[0] == test_number.replace("+", "")  # First arg is phone number without +
    assert args[1]['subject_name'] == expected_formatted  # Second arg is message_data
    
    # Test Twilio WhatsApp channel
    SystemParameter.objects.filter(parameter="channel").update(value=MessageChannel.TWILIO_WHATSAPP.value)
    result = message_service.send_message(test_number, test_message)
    assert mock_twilio_client.return_value.messages.create.call_args[1]['body'] == expected_formatted
    
    # Test Twilio SMS channel
    SystemParameter.objects.filter(parameter="channel").update(value=MessageChannel.TWILIO_SMS.value)
    result = message_service.send_message(test_number, test_message)
    assert mock_twilio_client.return_value.messages.create.call_args[1]['body'] == expected_formatted

@pytest.mark.django_db
@override_settings(**TWILIO_TEST_SETTINGS)
def test_phone_number_formatting_in_send_message(message_service, mock_twilio_client, mock_whatsapp_provider):
    test_message = "Test message"
    test_number = "+5212345678901"
    
    # Test Meta WhatsApp channel (number should remain unchanged)
    SystemParameter.objects.get_or_create(parameter="channel", defaults={"value": MessageChannel.META_WHATSAPP.value})
    message_service.send_message(test_number, test_message)
    
    # Verify the phone number was formatted correctly
    mock_whatsapp_provider.send_message.assert_called_once()
    args, kwargs = mock_whatsapp_provider.send_message.call_args
    assert args[0] == "5212345678901"  # WhatsApp provider removes '+'
    
    # Test Twilio WhatsApp channel (should add whatsapp: prefix and format number)
    SystemParameter.objects.filter(parameter="channel").update(value=MessageChannel.TWILIO_WHATSAPP.value)
    message_service.send_message(test_number, test_message)
    assert mock_twilio_client.return_value.messages.create.call_args[1]['to'] == "whatsapp:+52112345678901"
    
    # Test Twilio SMS channel (should format number)
    SystemParameter.objects.filter(parameter="channel").update(value=MessageChannel.TWILIO_SMS.value)
    message_service.send_message(test_number, test_message)
    assert mock_twilio_client.return_value.messages.create.call_args[1]['to'] == "+52112345678901" 