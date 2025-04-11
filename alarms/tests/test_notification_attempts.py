from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from subjects.models import Subject
from custodians.models import Custodian
from ..models import Alarm, NotificationAttempt, NotificationStatus
from django.utils import timezone
from datetime import date

User = get_user_model()

@override_settings(
    SECURE_SSL_REDIRECT=False,
    SECURE_PROXY_SSL_HEADER=None,
    SESSION_COOKIE_SECURE=False,
    CSRF_COOKIE_SECURE=False,
    SECURE_HSTS_SECONDS=0,
    SECURE_HSTS_INCLUDE_SUBDOMAINS=False,
    SECURE_HSTS_PRELOAD=False
)
class NotificationAttemptTests(TestCase):
    def setUp(self):
        # Create test users
        self.staff_user = User.objects.create_user(
            username='staff',
            password='staffpass123',
            is_staff=True,
            email='staff@test.com'
        )
        self.custodian_user = User.objects.create_user(
            username='custodian',
            password='custodianpass123',
            email='custodian@test.com',
            first_name='Test',
            last_name='Custodian'
        )
        
        # Update custodian (created by signal) with phone number
        self.custodian = Custodian.objects.get(user=self.custodian_user)
        self.custodian.phone_number = '+1234567890'
        self.custodian.save()
        
        # Create subject
        self.subject = Subject.objects.create(
            name='Test Subject',
            custodian=self.custodian,
            date_of_birth=date(2000, 1, 1),
            gender='M'
        )
        
        # Create alarm
        self.alarm = Alarm.objects.create(
            subject=self.subject,
            timestamp=timezone.now(),
            notification_status=NotificationStatus.PENDING
        )
        
        # Create notification attempt
        self.notification_attempt = NotificationAttempt.objects.create(
            alarm=self.alarm,
            recipient=self.custodian,
            channel='whatsapp',
            status=NotificationStatus.PENDING
        )
        
        # Setup API client
        self.client = APIClient()
        
    def test_list_notification_attempts_staff(self):
        """Test that staff can list all notification attempts"""
        self.client.force_authenticate(user=self.staff_user)
        url = reverse('alarms_api:notification-attempt-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_list_notification_attempts_custodian(self):
        """Test that custodians can only see their own notification attempts"""
        self.client.force_authenticate(user=self.custodian_user)
        url = reverse('alarms_api:notification-attempt-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_retrieve_notification_attempt(self):
        """Test retrieving a specific notification attempt"""
        self.client.force_authenticate(user=self.staff_user)
        url = reverse('alarms_api:notification-attempt-detail', args=[self.notification_attempt.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.notification_attempt.id)
        
    def test_mark_notification_sent(self):
        """Test marking a notification as sent"""
        self.client.force_authenticate(user=self.staff_user)
        url = reverse('alarms_api:notification-attempt-mark-sent', args=[self.notification_attempt.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify the status was updated
        self.notification_attempt.refresh_from_db()
        self.assertEqual(self.notification_attempt.status, NotificationStatus.SENT)
        
    def test_mark_notification_failed(self):
        """Test marking a notification as failed"""
        self.client.force_authenticate(user=self.staff_user)
        url = reverse('alarms_api:notification-attempt-mark-failed', args=[self.notification_attempt.id])
        response = self.client.post(url, {'error_message': 'Test error'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify the status and error message were updated
        self.notification_attempt.refresh_from_db()
        self.assertEqual(self.notification_attempt.status, NotificationStatus.FAILED)
        self.assertEqual(self.notification_attempt.error_message, 'Test error')
        
    def test_unauthorized_access(self):
        """Test that unauthorized users cannot access notification attempts"""
        url = reverse('alarms_api:notification-attempt-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_custodian_cannot_access_other_notifications(self):
        """Test that custodians cannot access notification attempts for other subjects"""
        # Create another custodian and subject
        other_user = User.objects.create_user(
            username='other',
            password='otherpass123',
            email='other@test.com'
        )
        other_custodian = Custodian.objects.get(user=other_user)
        other_custodian.phone_number = '+0987654321'
        other_custodian.save()
        
        other_subject = Subject.objects.create(
            name='Other Subject',
            custodian=other_custodian,
            date_of_birth=date(2000, 1, 1),
            gender='F'
        )
        other_alarm = Alarm.objects.create(
            subject=other_subject,
            timestamp=timezone.now()
        )
        other_attempt = NotificationAttempt.objects.create(
            alarm=other_alarm,
            recipient=other_custodian,
            channel='whatsapp',
            status=NotificationStatus.PENDING
        )
        
        # Try to access the other notification attempt
        self.client.force_authenticate(user=self.custodian_user)
        url = reverse('alarms_api:notification-attempt-detail', args=[other_attempt.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) 