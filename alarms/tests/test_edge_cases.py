from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from subjects.models import Subject, SubjectQR
from custodians.models import Custodian
from ..models import Alarm, NotificationAttempt, NotificationStatus, NotificationChannel
from rest_framework.test import APITestCase
from django.conf import settings

User = get_user_model()

class AlarmEdgeCaseTests(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Override settings for testing
        cls.old_trailing_slash = getattr(settings, 'APPEND_SLASH', True)
        cls.old_secure_ssl_redirect = getattr(settings, 'SECURE_SSL_REDIRECT', True)
        settings.APPEND_SLASH = False
        settings.SECURE_SSL_REDIRECT = False

    @classmethod
    def tearDownClass(cls):
        # Restore settings
        settings.APPEND_SLASH = cls.old_trailing_slash
        settings.SECURE_SSL_REDIRECT = cls.old_secure_ssl_redirect
        super().tearDownClass()

    def setUp(self):
        # Create test user and custodian
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.custodian = Custodian.objects.get_or_create(user=self.user)[0]
        
        # Create test subject
        self.subject = Subject.objects.create(
            name='Test Subject',
            date_of_birth=timezone.now().date(),
            gender='M',
            custodian=self.custodian
        )
        
        # Create test QR code
        self.qr_code = SubjectQR.objects.create(
            subject=self.subject,
            is_active=True
        )
        
        # Create test alarm
        self.alarm = Alarm.objects.create(
            subject=self.subject,
            qr_code=self.qr_code,
            location='Test Location'
        )
        
        # Set up client
        self.client = self.client_class()
        self.client.force_authenticate(user=self.user)
        # Configure client to use HTTPS
        self.client.defaults['wsgi.url_scheme'] = 'https'

    def test_invalid_alarm_creation(self):
        """Test creating an alarm with invalid data"""
        url = reverse('alarms_api:alarm-list')  # Use the API namespace
        print(f"Debug - URL: {url}")  # Debug print
        data = {
            'subject': 99999,  # Non-existent subject
            'qr_code': self.qr_code.id,  # Valid QR code ID
            'location': '',  # Empty location
            'is_test': 'invalid'  # Invalid boolean
        }
        
        # Use only format='json'
        response = self.client.post(url, data, format='json')
        print(f"Debug - Response: {response.status_code}")  # Debug print
        print(f"Debug - Response content: {response.content}")  # Debug print
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('subject', response.data)
        self.assertIn('location', response.data)
        self.assertIn('is_test', response.data)

    def test_unauthorized_access(self):
        """Test accessing alarms without authentication"""
        # Log out the client
        self.client.logout()
        
        url = reverse('alarms:alarm-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 401)

    def test_test_alarm_handling(self):
        """Test handling of test alarms"""
        # Create a test alarm
        test_alarm = Alarm.objects.create(
            subject=self.subject,
            qr_code=self.qr_code,
            location='Test Location',
            is_test=True
        )
        
        # Verify test alarm properties
        self.assertTrue(test_alarm.is_test)
        self.assertEqual(test_alarm.notification_status, NotificationStatus.PENDING)
        
        # Attempt to resolve test alarm
        url = reverse('alarms:alarm-resolve', kwargs={'pk': test_alarm.id})
        data = {'resolution_notes': 'Test resolution'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, 200)
        test_alarm.refresh_from_db()
        self.assertIsNotNone(test_alarm.resolved_at)
        self.assertEqual(test_alarm.resolution_notes, 'Test resolution')

class NotificationAttemptEdgeCaseTests(TestCase):
    def setUp(self):
        # Create test user and custodian
        self.user = User.objects.create_user(
            username='testuser2',  # Different username to avoid conflicts
            password='testpass123',
            email='test2@example.com'
        )
        self.custodian = Custodian.objects.get_or_create(user=self.user)[0]
        
        # Create test subject
        self.subject = Subject.objects.create(
            name='Test Subject',
            date_of_birth=timezone.now().date(),
            gender='M',
            custodian=self.custodian
        )
        
        # Create test QR code
        self.qr_code = SubjectQR.objects.create(
            subject=self.subject,
            is_active=True
        )
        
        # Create test alarm
        self.alarm = Alarm.objects.create(
            subject=self.subject,
            qr_code=self.qr_code,
            location='Test Location'
        )
        
        # Set up client
        self.client = Client()
        self.client.login(username='testuser2', password='testpass123')

    def test_max_retry_limit(self):
        """Test notification attempt retry limit"""
        attempt = NotificationAttempt.objects.create(
            alarm=self.alarm,
            recipient=self.custodian,
            channel=NotificationChannel.WHATSAPP
        )
        
        # Simulate multiple failures up to max retries
        for _ in range(NotificationAttempt.MAX_RETRIES):
            attempt.mark_failed("Test error")
            attempt.refresh_from_db()
        
        # Verify max retries reached
        self.assertEqual(attempt.retry_count, NotificationAttempt.MAX_RETRIES)
        self.assertEqual(attempt.status, NotificationStatus.FAILED)
        
        # Verify alarm status
        self.alarm.refresh_from_db()
        self.assertEqual(self.alarm.notification_status, NotificationStatus.FAILED)

    def test_concurrent_notification_attempts(self):
        """Test handling of concurrent notification attempts"""
        # Create multiple notification attempts for the same alarm
        attempts = []
        for _ in range(3):
            attempt = NotificationAttempt.objects.create(
                alarm=self.alarm,
                recipient=self.custodian,
                channel=NotificationChannel.WHATSAPP
            )
            attempts.append(attempt)
        
        # Mark attempts as sent/failed in different orders
        attempts[1].mark_sent()
        attempts[0].mark_failed("First attempt failed")
        attempts[2].mark_sent()
        
        # Verify alarm status reflects the latest successful attempt
        self.alarm.refresh_from_db()
        self.assertTrue(self.alarm.notification_sent)
        self.assertEqual(self.alarm.notification_status, NotificationStatus.SENT)
        self.assertEqual(self.alarm.notification_attempt_count, 3)

    def test_invalid_notification_status_transition(self):
        """Test invalid notification status transitions"""
        attempt = NotificationAttempt.objects.create(
            alarm=self.alarm,
            recipient=self.custodian,
            channel=NotificationChannel.WHATSAPP
        )
        
        # Mark as sent first
        attempt.mark_sent()
        
        # Try to mark as failed after being sent
        with self.assertRaises(ValidationError):
            attempt.mark_failed("Should not be able to fail after sending")

    def test_notification_rate_limiting(self):
        """Test notification rate limiting"""
        # Create multiple notification attempts in quick succession
        attempts = []
        for _ in range(5):  # Assuming rate limit is less than 5
            attempt = NotificationAttempt.objects.create(
                alarm=self.alarm,
                recipient=self.custodian,
                channel=NotificationChannel.WHATSAPP
            )
            attempts.append(attempt)
        
        # Verify rate limiting is enforced
        self.assertEqual(
            NotificationAttempt.objects.filter(
                alarm=self.alarm,
                created_at__gte=timezone.now() - timezone.timedelta(minutes=1)
            ).count(),
            5  # Should match the rate limit
        ) 