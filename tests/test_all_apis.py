from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User
from custodians.models import Custodian
from subjects.models import Subject
from alarms.models import Alarm, NotificationAttempt, NotificationChannel, NotificationStatus
from django.urls import reverse
from datetime import date
import json

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
        
        # Create test alarms
        self.alarm1 = Alarm.objects.create(
            subject=self.subject1,
            location='Test Location 1',
            is_test=False
        )
        self.alarm2 = Alarm.objects.create(
            subject=self.subject2,
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

        # Set up API client
        self.client = APIClient()
        # Configure client to use HTTPS
        self.client.defaults.update({
            'wsgi.url_scheme': 'https',
            'HTTP_X_FORWARDED_PROTO': 'https',
            'SERVER_NAME': 'keryu.mx',
            'SERVER_PORT': '443'
        })

    def test_auth_token(self):
        """Test authentication token endpoint"""
        url = reverse('token_obtain_pair')
        data = {
            'username': 'testuser1',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        return response.data['access']

    def test_subjects_api(self):
        """Test the subjects API endpoints."""
        # Get authentication token
        token = self.test_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # List subjects
        response = self.client.get(reverse('subjects_api:subject_list_api'), follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Create a subject
        data = {
            'name': 'Test Subject',
            'date_of_birth': '2000-01-01',
            'gender': 'M',
            'custodian': self.custodian1.id
        }
        response = self.client.post(reverse('subjects_api:subject_list_api'), data, format='json', follow=True)
        self.assertEqual(response.status_code, 201)
        subject_id = response.data['id']
        
        # Get a subject
        response = self.client.get(reverse('subjects_api:subject_detail_api', args=[subject_id]), follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Update a subject
        data['name'] = 'Updated Subject'
        response = self.client.put(reverse('subjects_api:subject_detail_api', args=[subject_id]), data, format='json', follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Delete a subject
        response = self.client.delete(reverse('subjects_api:subject_detail_api', args=[subject_id]), follow=True)
        self.assertEqual(response.status_code, 204)

    def test_alarms_api(self):
        """Test the alarms API endpoints."""
        # Get authentication token
        token = self.test_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # List alarms
        response = self.client.get(reverse('alarms_api:alarm-list'), follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Create an alarm
        data = {
            'subject': self.subject1.id,
            'location': 'Test Location',
            'is_test': False
        }
        response = self.client.post(reverse('alarms_api:alarm-list'), data, format='json', follow=True)
        self.assertEqual(response.status_code, 201)
        alarm_id = response.data['id']
        
        # Get an alarm
        response = self.client.get(reverse('alarms_api:alarm-detail', args=[alarm_id]), follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Update an alarm
        data['location'] = 'Updated Location'
        response = self.client.put(reverse('alarms_api:alarm-detail', args=[alarm_id]), data, format='json', follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Delete an alarm
        response = self.client.delete(reverse('alarms_api:alarm-detail', args=[alarm_id]), follow=True)
        self.assertEqual(response.status_code, 204)

    def test_notification_attempts_api(self):
        """Test the notification attempts API endpoints."""
        # Get authentication token
        token = self.test_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # List notification attempts
        response = self.client.get(reverse('alarms_api:notification-attempt-list'), follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Create a notification attempt
        data = {
            'alarm': self.alarm1.id,
            'recipient': self.custodian1.id,
            'channel': 'whatsapp'
        }
        response = self.client.post(reverse('alarms_api:notification-attempt-list'), data, format='json', follow=True)
        self.assertEqual(response.status_code, 201)
        notification_id = response.data['id']
        
        # Get a notification attempt
        response = self.client.get(reverse('alarms_api:notification-attempt-detail', args=[notification_id]), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_custodians_api(self):
        """Test the custodians API endpoints."""
        # Get authentication token
        token = self.test_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # List custodians
        response = self.client.get(reverse('custodians_api:custodian_list_api'), follow=True)
        self.assertEqual(response.status_code, 200)
        
        # Get a custodian
        response = self.client.get(reverse('custodians_api:custodian_detail_api', args=[self.custodian1.id]), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_error_handling(self):
        """Test API error handling"""
        # Get authentication token
        token = self.test_auth_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Test not found
        response = self.client.get(reverse('subjects_api:subject_detail_api', args=[999]), follow=True)
        self.assertEqual(response.status_code, 404)
        
        # Test unauthorized access (clear credentials)
        self.client.credentials()
        response = self.client.get(reverse('subjects_api:subject_list_api'), follow=True)
        self.assertEqual(response.status_code, 401)

    def test_rate_limiting(self):
        """Test rate limiting on API endpoints."""
        # Test rate limiting on subjects endpoint
        for _ in range(1001):  # Exceed the anonymous rate limit
            response = self.client.get(reverse('subjects_api:subject_list_api'), follow=True)
        
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
        
        # Simulate Twilio webhook
        data = {
            'MessageSid': 'test_message_sid',
            'MessageStatus': 'delivered',
            'To': str(self.custodian1.phone_number),
            'From': '+1234567890',
            'SmsSid': 'test_message_sid',
            'SmsStatus': 'delivered',
            'AccountSid': 'test_account_sid'
        }
        response = self.client.post(reverse('twilio_status_callback'), data=json.dumps(data), content_type='application/json', follow=True)
        self.assertEqual(response.status_code, 200) 