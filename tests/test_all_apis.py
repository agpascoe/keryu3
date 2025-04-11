from django.test import TestCase, override_settings
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from custodians.models import Custodian
from subjects.models import Subject, SubjectQR
from alarms.models import Alarm, NotificationAttempt, NotificationChannel, NotificationStatus
from django.urls import reverse
from datetime import date, timedelta
from django.utils import timezone
import json

@override_settings(
    SECURE_SSL_REDIRECT=True,
    SESSION_COOKIE_SECURE=True,
    CSRF_COOKIE_SECURE=True,
    SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO', 'https'),
    SECURE_HSTS_SECONDS=31536000,
    SECURE_HSTS_INCLUDE_SUBDOMAINS=True,
    SECURE_HSTS_PRELOAD=True,
)
class TestAllAPIs(APITestCase):
    """Comprehensive test suite for all API endpoints"""

    def setUp(self):
        """Set up test data"""
        # Create test users
        self.user1 = User.objects.create_user(username='testuser1', password='testpass123')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass123')
        
        # Get the automatically created custodians
        self.custodian1 = self.user1.custodian
        self.custodian2 = self.user2.custodian
        
        # Update custodian data
        self.custodian1.phone_number = '+1234567890'
        self.custodian1.save()
        self.custodian2.phone_number = '+0987654321'
        self.custodian2.save()
        
        # Create test subjects
        self.subject1 = Subject.objects.create(
            name='Test Subject 1',
            date_of_birth=date(2000, 1, 1),
            gender='M',
            custodian=self.custodian1
        )
        self.subject2 = Subject.objects.create(
            name='Test Subject 2',
            date_of_birth=date(2000, 1, 2),
            gender='F',
            custodian=self.custodian2
        )
        
        # Create test QR codes
        self.qr_code1 = SubjectQR.objects.create(
            subject=self.subject1,
            is_active=True
        )
        self.qr_code2 = SubjectQR.objects.create(
            subject=self.subject2,
            is_active=True
        )
        
        # Create test alarms
        self.alarm1 = Alarm.objects.create(
            subject=self.subject1,
            qr_code=self.qr_code1,
            location='Test Location 1',
            is_test=False
        )
        self.alarm2 = Alarm.objects.create(
            subject=self.subject2,
            qr_code=self.qr_code2,
            location='Test Location 2',
            is_test=False
        )
        
        # Create test notification attempts
        self.notification1 = NotificationAttempt.objects.create(
            alarm=self.alarm1,
            recipient=self.custodian1,
            channel=NotificationChannel.WHATSAPP,
            status=NotificationStatus.PENDING
        )
        self.notification2 = NotificationAttempt.objects.create(
            alarm=self.alarm2,
            recipient=self.custodian2,
            channel=NotificationChannel.WHATSAPP,
            status=NotificationStatus.PENDING
        )

        # Set up API client with HTTPS configuration
        self.client = APIClient()
        self.client.defaults.update({
            'wsgi.url_scheme': 'https',
            'HTTP_X_FORWARDED_PROTO': 'https',
            'SERVER_NAME': 'keryu.mx',
            'SERVER_PORT': '443',
            'HTTP_HOST': 'keryu.mx',
            'HTTP_X_FORWARDED_HOST': 'keryu.mx',
            'HTTP_X_FORWARDED_FOR': '127.0.0.1'
        })
        
        # Get authentication token and set credentials
        url = reverse('token_obtain_pair')
        data = {
            'username': 'testuser1',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json', secure=True)
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_auth_token(self):
        """Test authentication token endpoint"""
        url = reverse('token_obtain_pair')
        data = {
            'username': 'testuser1',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json', secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        return response.data['access']

    def test_subjects_api(self):
        """Test the subjects API endpoints."""
        # List subjects
        response = self.client.get(reverse('subjects_api:subject_list_api'), secure=True)
        self.assertEqual(response.status_code, 200)
        
        # Create a subject
        data = {
            'name': 'Test Subject',
            'date_of_birth': '2000-01-01',
            'gender': 'M',
            'custodian': self.custodian1.id
        }
        response = self.client.post(reverse('subjects_api:subject_list_api'), data, format='json', secure=True)
        self.assertEqual(response.status_code, 201)
        subject_id = response.data['id']
        
        # Get a subject
        response = self.client.get(reverse('subjects_api:subject_detail_api', args=[subject_id]), secure=True)
        self.assertEqual(response.status_code, 200)
        
        # Update a subject
        data['name'] = 'Updated Subject'
        response = self.client.put(reverse('subjects_api:subject_detail_api', args=[subject_id]), data, format='json', secure=True)
        self.assertEqual(response.status_code, 200)
        
        # Delete a subject
        response = self.client.delete(reverse('subjects_api:subject_detail_api', args=[subject_id]), secure=True)
        self.assertEqual(response.status_code, 204)

    def test_alarms_api(self):
        """Test the alarms API endpoints."""
        # List alarms
        response = self.client.get(reverse('alarms_api:alarm-list'), secure=True)
        self.assertEqual(response.status_code, 200)
        
        # Create an alarm
        data = {
            'subject': self.subject1.id,
            'qr_code': self.qr_code1.id,
            'location': 'Test Location',
            'is_test': False
        }
        response = self.client.post(reverse('alarms_api:alarm-list'), data, format='json', secure=True)
        self.assertEqual(response.status_code, 201)
        alarm_id = response.data['id']
        
        # Get an alarm
        response = self.client.get(reverse('alarms_api:alarm-detail', args=[alarm_id]), secure=True)
        self.assertEqual(response.status_code, 200)
        
        # Update an alarm
        data['location'] = 'Updated Location'
        response = self.client.put(reverse('alarms_api:alarm-detail', args=[alarm_id]), data, format='json', secure=True)
        self.assertEqual(response.status_code, 200)
        
        # Delete an alarm
        response = self.client.delete(reverse('alarms_api:alarm-detail', args=[alarm_id]), secure=True)
        self.assertEqual(response.status_code, 204)

        # Test resolve alarm endpoint
        response = self.client.post(reverse('alarms_api:alarm-resolve', args=[self.alarm1.id]), 
                                  {'resolution_notes': 'Test resolution'}, 
                                  format='json', 
                                  secure=True)
        self.assertEqual(response.status_code, 200)
        self.alarm1.refresh_from_db()
        self.assertIsNotNone(self.alarm1.resolved_at)

        # Test alarm statistics endpoint
        response = self.client.get(reverse('alarms_api:alarm-statistics'), secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_alarms', response.data)
        self.assertIn('recent_alarms', response.data)
        self.assertIn('subject_stats', response.data)
        self.assertIn('date_stats', response.data)
        self.assertIn('notifications', response.data)

        # Test retry notification endpoint
        response = self.client.post(reverse('alarms_api:retry-notification', args=[self.alarm1.id]), 
                                  format='json', 
                                  secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.data)

    def test_notification_attempts_api(self):
        """Test the notification attempts API endpoints."""
        # List notification attempts
        response = self.client.get(reverse('alarms_api:notification-attempt-list'), secure=True)
        self.assertEqual(response.status_code, 200)
        
        # Create a notification attempt
        data = {
            'alarm': self.alarm1.id,
            'recipient': self.custodian1.id,
            'channel': 'whatsapp'
        }
        response = self.client.post(reverse('alarms_api:notification-attempt-list'), data, format='json', secure=True)
        self.assertEqual(response.status_code, 201)
        notification_id = response.data['id']
        
        # Get a notification attempt
        response = self.client.get(reverse('alarms_api:notification-attempt-detail', args=[notification_id]), secure=True)
        self.assertEqual(response.status_code, 200)

        # Test mark notification as sent
        response = self.client.post(reverse('alarms_api:notification-attempt-mark-sent', args=[notification_id]), 
                                  format='json', 
                                  secure=True)
        self.assertEqual(response.status_code, 200)
        
        # Get the updated notification attempt
        notification = NotificationAttempt.objects.get(id=notification_id)
        self.assertEqual(notification.status, NotificationStatus.SENT)

        # Test mark notification as failed
        response = self.client.post(reverse('alarms_api:notification-attempt-mark-failed', args=[notification_id]), 
                                  {'error_message': 'Test error'}, 
                                  format='json', 
                                  secure=True)
        self.assertEqual(response.status_code, 200)
        
        # Get the updated notification attempt
        notification = NotificationAttempt.objects.get(id=notification_id)
        self.assertEqual(notification.status, NotificationStatus.FAILED)

    def test_custodians_api(self):
        """Test the custodians API endpoints."""
        # List custodians
        response = self.client.get(reverse('custodians_api:custodian_list_api'), secure=True)
        self.assertEqual(response.status_code, 200)
        
        # Get a custodian
        response = self.client.get(reverse('custodians_api:custodian_detail_api', args=[self.custodian1.id]), secure=True)
        self.assertEqual(response.status_code, 200)

    def test_error_handling(self):
        """Test API error handling"""
        # Test not found
        response = self.client.get(reverse('subjects_api:subject_detail_api', args=[999]), secure=True)
        self.assertEqual(response.status_code, 404)
        
        # Test unauthorized access (clear credentials)
        self.client.credentials()
        response = self.client.get(reverse('subjects_api:subject_list_api'), secure=True)
        self.assertEqual(response.status_code, 401)

    def test_rate_limiting(self):
        """Test rate limiting on API endpoints."""
        # Test rate limiting on subjects endpoint
        for _ in range(1001):  # Exceed the anonymous rate limit
            response = self.client.get(reverse('subjects_api:subject_list_api'), secure=True)
        
        # The 1001st request should be rate limited
        self.assertEqual(response.status_code, 429)

    def test_twilio_webhook(self):
        """Test Twilio webhook endpoint."""
        # Create a notification attempt
        notification = NotificationAttempt.objects.create(
            alarm=self.alarm1,
            recipient=self.custodian1,
            channel='whatsapp',
            status=NotificationStatus.PENDING
        )
        
        # Set the message_sid on the alarm
        self.alarm1.message_sid = 'test_message_sid'
        self.alarm1.save()
        
        # Simulate Twilio webhook
        data = {
            'MessageSid': 'test_message_sid',
            'MessageStatus': 'delivered',
            'To': str(self.custodian1.phone_number),
            'From': '+1234567890',
            'ErrorCode': '',
            'ErrorMessage': ''
        }
        response = self.client.post(reverse('twilio_status_callback'), data=data, secure=True)
        self.assertEqual(response.status_code, 200) 