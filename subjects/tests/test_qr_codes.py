from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from custodians.models import Custodian, Subject
from subjects.models import SubjectQR, Alarm
from django.core.files.uploadedfile import SimpleUploadedFile
import uuid
import json
from unittest.mock import patch

class QRCodeTests(TestCase):
    def setUp(self):
        # Create test user and custodian
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.custodian = Custodian.objects.create(
            user=self.user,
            phone='+525591981815'
        )
        
        # Create test subject
        self.subject = Subject.objects.create(
            custodian=self.custodian,
            name='Test Subject',
            gender='M',
            birth_date='2000-01-01',
            is_active=True
        )
        
        # Create test QR code
        self.qr = SubjectQR.objects.create(
            subject=self.subject,
            uuid=uuid.uuid4(),
            is_active=True
        )
        
        # Create test client
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')

    def test_qr_codes_list_view(self):
        """Test QR codes list view"""
        response = self.client.get(reverse('subjects:qr_codes'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'subjects/qr_codes.html')
        self.assertContains(response, self.subject.name)
        self.assertContains(response, str(self.qr.uuid))

    def test_generate_qr_code(self):
        """Test QR code generation"""
        data = {
            'subject_id': self.subject.id,
            'activate': 'on'
        }
        response = self.client.post(
            reverse('subjects:generate_qr'),
            data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertTrue(SubjectQR.objects.filter(subject=self.subject).exists())

    def test_activate_deactivate_qr(self):
        """Test QR code activation and deactivation"""
        # Create another QR code
        qr2 = SubjectQR.objects.create(
            subject=self.subject,
            uuid=uuid.uuid4(),
            is_active=False
        )
        
        # Test activation
        response = self.client.post(
            reverse('subjects:activate_qr', args=[qr2.uuid]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        qr2.refresh_from_db()
        self.qr.refresh_from_db()
        self.assertTrue(qr2.is_active)
        self.assertFalse(self.qr.is_active)
        
        # Test deactivation
        response = self.client.post(
            reverse('subjects:deactivate_qr', args=[qr2.uuid]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        qr2.refresh_from_db()
        self.assertFalse(qr2.is_active)

    def test_delete_qr(self):
        """Test QR code deletion"""
        response = self.client.post(
            reverse('subjects:delete_qr', args=[self.qr.uuid]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(SubjectQR.objects.filter(id=self.qr.id).exists())

    @patch('subjects.tasks.send_whatsapp_notification.delay')
    def test_scan_qr(self, mock_send_notification):
        """Test QR code scanning"""
        # Test scanning active QR code
        response = self.client.get(
            reverse('subjects:scan_qr', args=[self.qr.uuid]) + 
            '?lat=19.4326&lng=-99.1332'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'subjects/scan_result.html')
        
        # Verify alarm creation
        alarm = Alarm.objects.last()
        self.assertIsNotNone(alarm)
        self.assertEqual(alarm.subject, self.subject)
        self.assertEqual(alarm.qr_code, self.qr)
        self.assertEqual(alarm.location, '19.4326,-99.1332')
        
        # Verify WhatsApp notification was queued
        mock_send_notification.assert_called_once_with(alarm.id)
        
        # Test scanning inactive QR code
        self.qr.is_active = False
        self.qr.save()
        response = self.client.get(reverse('subjects:scan_qr', args=[self.qr.uuid]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This QR code is no longer active')

    def test_qr_image_download(self):
        """Test QR code image viewing and downloading"""
        # Test viewing QR code image
        response = self.client.get(reverse('subjects:qr_image', args=[self.qr.uuid]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        
        # Test downloading QR code
        response = self.client.get(reverse('subjects:download_qr', args=[self.qr.uuid]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/png')
        self.assertTrue(response['Content-Disposition'].startswith('attachment')) 