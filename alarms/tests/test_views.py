from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from subjects.models import Subject, SubjectQR
from custodians.models import Custodian
from ..models import Alarm, NotificationAttempt, NotificationStatus, NotificationChannel
from rest_framework.test import APIClient

User = get_user_model()

class AlarmAPITests(TestCase):
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
        
        # Set up client with HTTPS
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.client.defaults['SERVER_NAME'] = 'keryu.mx'
        self.client.defaults['wsgi.url_scheme'] = 'https'
        self.client.defaults['HTTP_X_FORWARDED_PROTO'] = 'https'

    def test_create_alarm(self):
        """Test creating a new alarm via API"""
        url = reverse('alarms_api:alarm-list')
        data = {
            'subject': self.subject.id,
            'qr_code': self.qr_code.id,
            'location': 'New Location',
            'is_test': False
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Alarm.objects.count(), 2)  # Original + new
        self.assertEqual(response.data['location'], 'New Location')
        self.assertEqual(response.data['notification_status'], NotificationStatus.PENDING)

    def test_list_alarms(self):
        """Test listing alarms via API"""
        url = reverse('alarms_api:alarm-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.alarm.id)

    def test_retrieve_alarm(self):
        """Test retrieving a single alarm via API"""
        url = reverse('alarms_api:alarm-detail', kwargs={'pk': self.alarm.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.alarm.id)

    def test_resolve_alarm(self):
        """Test resolving an alarm via API"""
        url = reverse('alarms_api:alarm-resolve', kwargs={'pk': self.alarm.id})
        data = {'resolution_notes': 'Test resolution'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.alarm.refresh_from_db()
        self.assertIsNotNone(self.alarm.resolved_at)
        self.assertEqual(self.alarm.resolution_notes, 'Test resolution')

    def test_notification_attempts(self):
        """Test notification attempts endpoint"""
        # Create a notification attempt
        attempt = NotificationAttempt.objects.create(
            alarm=self.alarm,
            recipient=self.custodian,
            channel=NotificationChannel.WHATSAPP
        )
        
        url = reverse('alarms_api:notification-attempt-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], attempt.id)

class NotificationAttemptAPITests(TestCase):
    def setUp(self):
        # Create test user and custodian
        self.user = User.objects.create_user(
            username='testuser2',
            password='testpass123',
            email='test2@example.com'
        )
        self.custodian, _ = Custodian.objects.get_or_create(user=self.user)
        
        # Create test subject
        self.subject = Subject.objects.create(
            name='Test Subject 2',
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
        
        # Create test notification attempt
        self.attempt = NotificationAttempt.objects.create(
            alarm=self.alarm,
            recipient=self.custodian,
            channel=NotificationChannel.WHATSAPP
        )
        
        # Set up client with HTTPS
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.client.defaults['SERVER_NAME'] = 'keryu.mx'
        self.client.defaults['wsgi.url_scheme'] = 'https'
        self.client.defaults['HTTP_X_FORWARDED_PROTO'] = 'https'

    def test_list_notification_attempts(self):
        """Test listing notification attempts via API"""
        url = reverse('alarms_api:notification-attempt-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.attempt.id)

    def test_retrieve_notification_attempt(self):
        """Test retrieving a single notification attempt via API"""
        url = reverse('alarms_api:notification-attempt-detail', kwargs={'pk': self.attempt.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], self.attempt.id)

    def test_mark_notification_sent(self):
        """Test marking a notification attempt as sent via API"""
        url = reverse('alarms_api:notification-attempt-mark-sent', kwargs={'pk': self.attempt.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        self.attempt.refresh_from_db()
        self.assertEqual(self.attempt.status, NotificationStatus.SENT)
        self.assertIsNotNone(self.attempt.sent_at)

    def test_mark_notification_failed(self):
        """Test marking a notification attempt as failed via API"""
        url = reverse('alarms_api:notification-attempt-mark-failed', kwargs={'pk': self.attempt.id})
        data = {'error_message': 'Test error'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.attempt.refresh_from_db()
        self.assertEqual(self.attempt.status, NotificationStatus.FAILED)
        self.assertEqual(self.attempt.error_message, 'Test error') 