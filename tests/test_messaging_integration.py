import os
import pytest
from django.test import override_settings
from core.messaging import MessageService, MessageChannel
from core.models import SystemParameter
from custodians.models import Custodian
from subjects.models import Subject, Alarm
from django.contrib.auth.models import User
from django.utils import timezone
from unittest.mock import patch, MagicMock

# Test settings
TEST_SETTINGS = {
    'WHATSAPP_PHONE_NUMBER_ID': 'test_phone_number_id',
    'WHATSAPP_ACCESS_TOKEN': 'test_access_token',
    'TWILIO_ACCOUNT_SID': 'test_account_sid',
    'TWILIO_AUTH_TOKEN': 'test_auth_token',
    'TWILIO_PHONE_NUMBER': '+1234567890',
    'TWILIO_WHATSAPP_NUMBER': '+1234567890'
}

@pytest.fixture
def test_user():
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def test_custodian(test_user):
    return Custodian.objects.create(
        user=test_user,
        phone_number='+5212345678901',
        is_verified=True
    )

@pytest.fixture
def test_subject(test_custodian):
    return Subject.objects.create(
        name='Test Subject',
        custodian=test_custodian,
        birth_date='2000-01-01'
    )

@pytest.fixture
def test_alarm(test_subject):
    return Alarm.objects.create(
        subject=test_subject,
        timestamp=timezone.now(),
        location='Test Location'
    )

@pytest.fixture
def mock_whatsapp_provider():
    mock = MagicMock()
    mock.send_message.return_value = {
        'success': True,
        'message_id': 'test_message_id',
        'status': 'SENT',
        'status_code': 200
    }
    return mock

@pytest.fixture
def mock_twilio_client():
    mock = MagicMock()
    mock_message = MagicMock()
    mock_message.sid = 'test_sid'
    mock_message.status = 'sent'
    mock.messages.create.return_value = mock_message
    return mock

@pytest.mark.django_db
class TestMessagingIntegration:
    """Integration tests for the messaging system"""

    def test_meta_whatsapp_channel(self, test_alarm, mock_whatsapp_provider):
        """Test sending message through Meta WhatsApp API"""
        with patch('core.messaging.get_notification_service', return_value=mock_whatsapp_provider):
            # Set channel to Meta WhatsApp
            SystemParameter.objects.get_or_create(
                parameter='channel',
                defaults={'value': MessageChannel.META_WHATSAPP.value}
            )
            
            # Create message service
            service = MessageService()
            
            # Send test message
            result = service.send_message(
                to_number=test_alarm.subject.custodian.phone_number,
                message=f"Alert: {test_alarm.subject.name} has been located"
            )
            
            # Verify the result
            assert result['status'] == 'success'
            assert result['channel'] == 'meta_whatsapp'
            
            # Verify the mock was called correctly
            mock_whatsapp_provider.send_message.assert_called_once()
            args = mock_whatsapp_provider.send_message.call_args[0]
            assert args[0] == '5212345678901'  # Phone number without '+'

    def test_twilio_whatsapp_channel(self, test_alarm, mock_twilio_client):
        """Test sending message through Twilio WhatsApp"""
        with patch('core.messaging.Client', return_value=mock_twilio_client):
            # Set channel to Twilio WhatsApp
            SystemParameter.objects.filter(parameter='channel').update(
                value=MessageChannel.TWILIO_WHATSAPP.value
            )
            
            # Create message service
            service = MessageService()
            
            # Send test message
            result = service.send_message(
                to_number=test_alarm.subject.custodian.phone_number,
                message=f"Alert: {test_alarm.subject.name} has been located"
            )
            
            # Verify the result
            assert result['status'] == 'success'
            assert result['channel'] == 'twilio_whatsapp'
            
            # Verify the mock was called correctly
            mock_twilio_client.messages.create.assert_called_once()
            kwargs = mock_twilio_client.messages.create.call_args[1]
            assert kwargs['to'] == f"whatsapp:+52112345678901"  # Phone number with 'whatsapp:' prefix

    def test_twilio_sms_channel(self, test_alarm, mock_twilio_client):
        """Test sending message through Twilio SMS"""
        with patch('core.messaging.Client', return_value=mock_twilio_client):
            # Set channel to Twilio SMS
            SystemParameter.objects.filter(parameter='channel').update(
                value=MessageChannel.TWILIO_SMS.value
            )
            
            # Create message service
            service = MessageService()
            
            # Send test message
            result = service.send_message(
                to_number=test_alarm.subject.custodian.phone_number,
                message=f"Alert: {test_alarm.subject.name} has been located"
            )
            
            # Verify the result
            assert result['status'] == 'success'
            assert result['channel'] == 'twilio_sms'
            
            # Verify the mock was called correctly
            mock_twilio_client.messages.create.assert_called_once()
            kwargs = mock_twilio_client.messages.create.call_args[1]
            assert kwargs['to'] == '+52112345678901'  # Regular phone number format

    def test_channel_fallback(self, test_alarm, mock_whatsapp_provider, mock_twilio_client):
        """Test channel fallback mechanism"""
        with patch('core.messaging.get_notification_service', return_value=mock_whatsapp_provider), \
             patch('core.messaging.Client', return_value=mock_twilio_client):
            
            # Configure Meta WhatsApp to fail
            mock_whatsapp_provider.send_message.return_value = {
                'success': False,
                'error': 'API Error',
                'status_code': 500
            }
            
            # Set channel to Meta WhatsApp initially
            SystemParameter.objects.get_or_create(
                parameter='channel',
                defaults={'value': MessageChannel.META_WHATSAPP.value}
            )
            
            # Create message service
            service = MessageService()
            
            # Send test message
            result = service.send_message(
                to_number=test_alarm.subject.custodian.phone_number,
                message=f"Alert: {test_alarm.subject.name} has been located"
            )
            
            # Verify Meta WhatsApp failed
            assert result['status'] == 'error'
            assert result['channel'] == 'meta_whatsapp'
            
            # Switch to Twilio WhatsApp
            SystemParameter.objects.filter(parameter='channel').update(
                value=MessageChannel.TWILIO_WHATSAPP.value
            )
            
            # Send message again
            result = service.send_message(
                to_number=test_alarm.subject.custodian.phone_number,
                message=f"Alert: {test_alarm.subject.name} has been located"
            )
            
            # Verify Twilio WhatsApp succeeded
            assert result['status'] == 'success'
            assert result['channel'] == 'twilio_whatsapp'

    def test_message_formatting(self, test_alarm, mock_whatsapp_provider):
        """Test message formatting across channels"""
        with patch('core.messaging.get_notification_service', return_value=mock_whatsapp_provider):
            # Set channel to Meta WhatsApp
            SystemParameter.objects.get_or_create(
                parameter='channel',
                defaults={'value': MessageChannel.META_WHATSAPP.value}
            )
            
            # Create message service
            service = MessageService()
            
            # Test message with extra whitespace and line breaks
            test_message = """
            Alert:   Test   Subject
            has been    located
            at Test Location
            """
            
            # Send test message
            result = service.send_message(
                to_number=test_alarm.subject.custodian.phone_number,
                message=test_message
            )
            
            # Verify message was formatted correctly
            mock_whatsapp_provider.send_message.assert_called_once()
            args = mock_whatsapp_provider.send_message.call_args[0]
            assert 'Alert: Test Subject has been located at Test Location' in args[1]['subject_name'] 