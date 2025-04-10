from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from subjects.models import Subject, SubjectQR
from custodians.models import Custodian
from ..models import Alarm, NotificationAttempt, NotificationStatus, NotificationChannel

User = get_user_model()

class AlarmModelTests(TestCase):
    def setUp(self):
        # Create test user and custodian
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.custodian = Custodian.objects.create(user=self.user)
        
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

    def test_alarm_creation(self):
        """Test that an alarm can be created with required fields"""
        alarm = Alarm.objects.create(
            subject=self.subject,
            qr_code=self.qr_code,
            location='Test Location'
        )
        
        self.assertEqual(alarm.subject, self.subject)
        self.assertEqual(alarm.qr_code, self.qr_code)
        self.assertEqual(alarm.location, 'Test Location')
        self.assertFalse(alarm.is_test)
        self.assertFalse(alarm.notification_sent)
        self.assertEqual(alarm.notification_status, NotificationStatus.PENDING)
        self.assertEqual(alarm.notification_attempts, 0)

    def test_alarm_resolution(self):
        """Test alarm resolution workflow"""
        alarm = Alarm.objects.create(
            subject=self.subject,
            qr_code=self.qr_code,
            location='Test Location'
        )
        
        # Test resolution
        resolution_notes = "Test resolution notes"
        alarm.resolve(resolution_notes)
        
        self.assertIsNotNone(alarm.resolved_at)
        self.assertEqual(alarm.resolution_notes, resolution_notes)

    def test_alarm_str(self):
        """Test the string representation of an alarm"""
        alarm = Alarm.objects.create(
            subject=self.subject,
            qr_code=self.qr_code,
            location='Test Location'
        )
        
        expected = f"Alarm for {self.subject.name} at {alarm.timestamp}"
        self.assertEqual(str(alarm), expected)

    def test_alarm_ordering(self):
        """Test that alarms are ordered by timestamp in descending order"""
        # Create alarms with different timestamps
        alarm1 = Alarm.objects.create(
            subject=self.subject,
            qr_code=self.qr_code,
            location='Location 1'
        )
        alarm2 = Alarm.objects.create(
            subject=self.subject,
            qr_code=self.qr_code,
            location='Location 2'
        )
        
        # Verify ordering
        alarms = list(Alarm.objects.all())
        self.assertEqual(alarms[0], alarm2)
        self.assertEqual(alarms[1], alarm1)

class NotificationAttemptModelTests(TestCase):
    def setUp(self):
        # Create test user and custodian
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.custodian = Custodian.objects.create(user=self.user)
        
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

    def test_notification_attempt_creation(self):
        """Test that a notification attempt can be created"""
        attempt = NotificationAttempt.objects.create(
            alarm=self.alarm,
            recipient=self.custodian,
            channel=NotificationChannel.WHATSAPP
        )
        
        self.assertEqual(attempt.alarm, self.alarm)
        self.assertEqual(attempt.recipient, self.custodian)
        self.assertEqual(attempt.channel, NotificationChannel.WHATSAPP)
        self.assertEqual(attempt.status, NotificationStatus.PENDING)
        self.assertEqual(attempt.retry_count, 0)

    def test_notification_attempt_mark_sent(self):
        """Test marking a notification attempt as sent"""
        attempt = NotificationAttempt.objects.create(
            alarm=self.alarm,
            recipient=self.custodian,
            channel=NotificationChannel.WHATSAPP
        )
        
        attempt.mark_sent()
        
        self.assertEqual(attempt.status, NotificationStatus.SENT)
        self.assertIsNotNone(attempt.sent_at)

    def test_notification_attempt_mark_failed(self):
        """Test marking a notification attempt as failed"""
        attempt = NotificationAttempt.objects.create(
            alarm=self.alarm,
            recipient=self.custodian,
            channel=NotificationChannel.WHATSAPP
        )
        
        error_message = "Test error message"
        attempt.mark_failed(error_message)
        
        self.assertEqual(attempt.status, NotificationStatus.FAILED)
        self.assertEqual(attempt.error_message, error_message)
        self.assertEqual(attempt.retry_count, 1)

    def test_notification_attempt_str(self):
        """Test the string representation of a notification attempt"""
        attempt = NotificationAttempt.objects.create(
            alarm=self.alarm,
            recipient=self.custodian,
            channel=NotificationChannel.WHATSAPP
        )
        
        expected = f"Notification attempt for {self.alarm} to {self.custodian} via whatsapp"
        self.assertEqual(str(attempt), expected)

    def test_notification_attempt_ordering(self):
        """Test that notification attempts are ordered by sent_at in descending order"""
        # Create attempts with different sent_at times
        attempt1 = NotificationAttempt.objects.create(
            alarm=self.alarm,
            recipient=self.custodian,
            channel=NotificationChannel.WHATSAPP
        )
        attempt2 = NotificationAttempt.objects.create(
            alarm=self.alarm,
            recipient=self.custodian,
            channel=NotificationChannel.WHATSAPP
        )
        
        # Mark attempts as sent with different times
        attempt1.mark_sent()
        attempt2.mark_sent()
        
        # Verify ordering
        attempts = list(NotificationAttempt.objects.all())
        self.assertEqual(attempts[0], attempt2)
        self.assertEqual(attempts[1], attempt1)

class AlarmNotificationIntegrationTests(TestCase):
    def setUp(self):
        # Create test user and custodian
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.custodian = Custodian.objects.create(user=self.user)
        
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

    def test_notification_attempt_updates_alarm_status(self):
        """Test that notification attempt status updates affect alarm status"""
        # Create notification attempt
        attempt = NotificationAttempt.objects.create(
            alarm=self.alarm,
            recipient=self.custodian,
            channel=NotificationChannel.WHATSAPP
        )
        
        # Mark attempt as sent
        attempt.mark_sent()
        
        # Refresh alarm from database
        self.alarm.refresh_from_db()
        
        # Verify alarm status
        self.assertTrue(self.alarm.notification_sent)
        self.assertEqual(self.alarm.notification_status, NotificationStatus.SENT)
        self.assertEqual(self.alarm.notification_attempts, 1)

    def test_multiple_notification_attempts(self):
        """Test handling of multiple notification attempts"""
        # Create first attempt
        attempt1 = NotificationAttempt.objects.create(
            alarm=self.alarm,
            recipient=self.custodian,
            channel=NotificationChannel.WHATSAPP
        )
        
        # Mark first attempt as failed
        attempt1.mark_failed("First attempt failed")
        
        # Create second attempt
        attempt2 = NotificationAttempt.objects.create(
            alarm=self.alarm,
            recipient=self.custodian,
            channel=NotificationChannel.WHATSAPP
        )
        
        # Mark second attempt as sent
        attempt2.mark_sent()
        
        # Refresh alarm from database
        self.alarm.refresh_from_db()
        
        # Verify alarm status
        self.assertTrue(self.alarm.notification_sent)
        self.assertEqual(self.alarm.notification_status, NotificationStatus.SENT)
        self.assertEqual(self.alarm.notification_attempts, 2)
        
        # Verify attempt counts
        self.assertEqual(attempt1.retry_count, 1)
        self.assertEqual(attempt2.retry_count, 0) 