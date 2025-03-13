from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from custodians.models import Custodian
from django.utils import timezone
from datetime import date
from django.core.files.uploadedfile import SimpleUploadedFile
import json
from .models import Subject, SubjectQR, Alarm

class SubjectAdminViewsTest(TestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        # Create regular user (Custodian profile will be created automatically)
        self.regular_user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='regularpass123'
        )
        
        # Update the automatically created custodian profile
        self.custodian = self.regular_user.custodian
        self.custodian.phone_number = '+525591981815'  # Mexican phone number format
        self.custodian.save()
        
        # Create subject
        self.subject = Subject.objects.create(
            name='Test Subject',
            date_of_birth=date(2000, 1, 1),
            gender='M',
            custodian=self.custodian,
            doctor_name='Dr. Test',
            doctor_phone='+525591981815',  # Mexican phone number format
            doctor_speciality='General',
            doctor_address='123 Test St'
        )
        
        self.client = Client()

        # Common test data
        self.valid_subject_data = {
            'name': 'Test Subject',
            'date_of_birth': '2000-01-01',
            'gender': 'M',
            'custodian': self.custodian.pk,
            'medical_conditions': 'None',
            'allergies': 'None',
            'medications': 'None',
            'doctor_name': 'Dr. Test',
            'doctor_phone': '+525591981815',  # Mexican phone number format
            'doctor_speciality': 'General',
            'doctor_address': '123 Test St',
            'is_active': True
        }

    def test_subject_list_admin_access(self):
        """Test that only admin users can access the subject list"""
        # Test admin access
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('subjects:subject_list'))
        self.assertEqual(response.status_code, 200)
        
        # Test regular user access
        self.client.login(username='regular', password='regularpass123')
        response = self.client.get(reverse('subjects:subject_list'))
        self.assertEqual(response.status_code, 403)
        
        # Test anonymous access
        self.client.logout()
        response = self.client.get(reverse('subjects:subject_list'))
        self.assertEqual(response.status_code, 403)

    def test_subject_detail_admin_access(self):
        """Test that only admin users can access subject details"""
        # Test admin access
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('subjects:subject_detail', args=[self.subject.pk]))
        self.assertEqual(response.status_code, 200)
        
        # Test regular user access
        self.client.login(username='regular', password='regularpass123')
        response = self.client.get(reverse('subjects:subject_detail', args=[self.subject.pk]))
        self.assertEqual(response.status_code, 403)
        
        # Test anonymous access
        self.client.logout()
        response = self.client.get(reverse('subjects:subject_detail', args=[self.subject.pk]))
        self.assertEqual(response.status_code, 403)

    def test_subject_stats_admin_access(self):
        """Test that only admin users can access subject statistics"""
        # Test admin access
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('subjects:subject_stats'))
        self.assertEqual(response.status_code, 200)
        
        # Test regular user access
        self.client.login(username='regular', password='regularpass123')
        response = self.client.get(reverse('subjects:subject_stats'))
        self.assertEqual(response.status_code, 403)
        
        # Test anonymous access
        self.client.logout()
        response = self.client.get(reverse('subjects:subject_stats'))
        self.assertEqual(response.status_code, 403)

    def test_qr_codes_admin_access(self):
        """Test that only admin users can access QR codes"""
        # Test admin access
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(reverse('subjects:qr_codes'))
        self.assertEqual(response.status_code, 200)
        
        # Test regular user access
        self.client.login(username='regular', password='regularpass123')
        response = self.client.get(reverse('subjects:qr_codes'))
        self.assertEqual(response.status_code, 403)
        
        # Test anonymous access
        self.client.logout()
        response = self.client.get(reverse('subjects:qr_codes'))
        self.assertEqual(response.status_code, 403)

    def test_subject_create(self):
        """Test subject creation"""
        self.client.login(username='admin', password='adminpass123')
        
        # Test GET request
        response = self.client.get(reverse('subjects:subject_create'))
        self.assertEqual(response.status_code, 200)
        
        # Test POST request with valid data
        data = self.valid_subject_data.copy()
        data.update({
            'name': 'New Subject',
            'doctor_name': 'Dr. New',
            'doctor_phone': '+525591981816',  # Different Mexican phone number
        })
        
        response = self.client.post(reverse('subjects:subject_create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Verify subject was created
        subject = Subject.objects.get(name='New Subject')
        self.assertEqual(subject.doctor_name, 'Dr. New')
        self.assertEqual(str(subject.doctor_phone), '+525591981816')

    def test_subject_edit(self):
        """Test subject editing"""
        self.client.login(username='admin', password='adminpass123')
        
        # Test GET request
        response = self.client.get(reverse('subjects:subject_edit', args=[self.subject.pk]))
        self.assertEqual(response.status_code, 200)
        
        # Test POST request with valid data
        data = self.valid_subject_data.copy()
        data.update({
            'name': 'Updated Subject',
            'doctor_name': 'Dr. Updated',
            'doctor_phone': '+525591981817',  # Different Mexican phone number
        })
        
        response = self.client.post(reverse('subjects:subject_edit', args=[self.subject.pk]), data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Verify subject was updated
        subject = Subject.objects.get(pk=self.subject.pk)
        self.assertEqual(subject.name, 'Updated Subject')
        self.assertEqual(subject.doctor_name, 'Dr. Updated')
        self.assertEqual(str(subject.doctor_phone), '+525591981817')

    def test_subject_delete(self):
        """Test subject deletion"""
        self.client.login(username='admin', password='adminpass123')
        
        # Test GET request (confirmation page)
        response = self.client.get(reverse('subjects:subject_delete', args=[self.subject.pk]))
        self.assertEqual(response.status_code, 200)
        
        # Test POST request (actual deletion)
        response = self.client.post(reverse('subjects:subject_delete', args=[self.subject.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Verify subject was deleted
        with self.assertRaises(Subject.DoesNotExist):
            Subject.objects.get(pk=self.subject.pk)

class SubjectManagementIntegrationTest(TestCase):
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        # Create multiple custodians
        self.custodian1 = User.objects.create_user(
            username='custodian1',
            email='custodian1@example.com',
            password='custodian1pass'
        ).custodian
        self.custodian1.phone_number = '+525591981815'
        self.custodian1.save()
        
        self.custodian2 = User.objects.create_user(
            username='custodian2',
            email='custodian2@example.com',
            password='custodian2pass'
        ).custodian
        self.custodian2.phone_number = '+525591981816'
        self.custodian2.save()
        
        # Create a test image file
        self.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\xff\xff\xff,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;',  # Small valid GIF image
            content_type='image/gif'
        )
        
        self.client = Client()
        self.client.login(username='admin', password='adminpass123')

    def test_complete_subject_workflow(self):
        """
        Test the entire subject management workflow:
        1. Create multiple subjects
        2. View subject list and verify stats
        3. Edit a subject
        4. View subject details
        5. Generate QR codes
        6. Delete a subject
        7. Verify statistics update
        """
        # 1. Create first subject
        response = self.client.post(reverse('subjects:subject_create'), {
            'name': 'John Doe',
            'date_of_birth': '2000-01-01',
            'gender': 'M',
            'custodian': self.custodian1.pk,
            'medical_conditions': 'Asthma',
            'allergies': 'Peanuts',
            'medications': 'Inhaler',
            'doctor_name': 'Dr. Smith',
            'doctor_phone': '+525591981817',
            'doctor_speciality': 'Pediatrician',
            'doctor_address': '123 Medical St',
            'photo': self.test_image,
            'is_active': True
        })
        self.assertEqual(response.status_code, 302)
        subject1 = Subject.objects.get(name='John Doe')
        
        # Create second subject
        response = self.client.post(reverse('subjects:subject_create'), {
            'name': 'Jane Doe',
            'date_of_birth': '2001-02-02',
            'gender': 'F',
            'custodian': self.custodian2.pk,
            'medical_conditions': 'None',
            'allergies': 'None',
            'medications': 'None',
            'doctor_name': 'Dr. Johnson',
            'doctor_phone': '+525591981818',
            'doctor_speciality': 'General',
            'doctor_address': '456 Medical Ave',
            'is_active': True
        })
        self.assertEqual(response.status_code, 302)
        subject2 = Subject.objects.get(name='Jane Doe')
        
        # 2. Check subject list and stats
        response = self.client.get(reverse('subjects:subject_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe')
        self.assertContains(response, 'Jane Doe')
        
        # Check statistics
        response = self.client.get(reverse('subjects:subject_stats'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<p class="card-text display-6">2</p>')  # Total subjects
        
        # 3. Edit first subject
        response = self.client.post(
            reverse('subjects:subject_edit', args=[subject1.pk]),
            {
                'name': 'John Doe Jr',
                'date_of_birth': '2000-01-01',
                'gender': 'M',
                'custodian': self.custodian1.pk,
                'medical_conditions': 'Asthma, Diabetes',
                'allergies': 'Peanuts, Shellfish',
                'medications': 'Inhaler, Insulin',
                'doctor_name': 'Dr. Smith',
                'doctor_phone': '+525591981817',
                'doctor_speciality': 'Pediatrician',
                'doctor_address': '123 Medical St',
                'is_active': True
            }
        )
        self.assertEqual(response.status_code, 302)
        
        # 4. Check subject details
        response = self.client.get(reverse('subjects:subject_detail', args=[subject1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe Jr')
        self.assertContains(response, 'Diabetes')
        
        # 5. Check QR codes page
        response = self.client.get(reverse('subjects:qr_codes'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe Jr')
        self.assertContains(response, 'Jane Doe')
        
        # 6. Delete second subject
        response = self.client.post(reverse('subjects:subject_delete', args=[subject2.pk]))
        self.assertEqual(response.status_code, 302)
        
        # 7. Verify updated statistics
        response = self.client.get(reverse('subjects:subject_stats'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<p class="card-text display-6">1</p>')  # Total subjects
        
        # Verify gender distribution
        self.assertContains(response, '<td>M</td>')
        self.assertContains(response, '<td>1</td>')
        self.assertContains(response, '<td>100.0%</td>')
        
        # Final verification of subject list
        response = self.client.get(reverse('subjects:subject_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'John Doe Jr')
        self.assertNotContains(response, 'Jane Doe')

    def test_error_handling(self):
        """Test error handling in the subject management workflow"""
        # Test invalid phone number format
        response = self.client.post(reverse('subjects:subject_create'), {
            'name': 'Test Subject',
            'date_of_birth': '2000-01-01',
            'gender': 'M',
            'custodian': self.custodian1.pk,
            'doctor_name': 'Dr. Test',
            'doctor_phone': 'invalid-phone',  # Invalid phone format
            'doctor_speciality': 'General',
            'doctor_address': '123 Test St',
            'is_active': True
        })
        self.assertEqual(response.status_code, 200)  # Form redisplay
        self.assertContains(response, 'Enter a valid phone number')
        
        # Test accessing non-existent subject
        response = self.client.get(reverse('subjects:subject_detail', args=[999]))
        self.assertEqual(response.status_code, 404)
        
        # Test deleting non-existent subject
        response = self.client.post(reverse('subjects:subject_delete', args=[999]))
        self.assertEqual(response.status_code, 404)
        
        # Test editing with missing required fields
        subject = Subject.objects.create(
            name='Test Subject',
            date_of_birth=date(2000, 1, 1),
            gender='M',
            custodian=self.custodian1,
            doctor_name='Dr. Test',
            doctor_phone='+525591981819',
            doctor_speciality='General',
            doctor_address='123 Test St'
        )
        
        response = self.client.post(
            reverse('subjects:subject_edit', args=[subject.pk]),
            {
                'name': '',  # Required field missing
                'date_of_birth': '2000-01-01',
                'gender': 'M',
                'custodian': self.custodian1.pk
            }
        )
        self.assertEqual(response.status_code, 200)  # Form redisplay
        self.assertContains(response, 'This field is required')

class SubjectTests(TestCase):
    def setUp(self):
        # Create test user and custodian
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.custodian = self.user.custodian
        
        # Create test subject
        self.subject = Subject.objects.create(
            name='Test Subject',
            date_of_birth=date(2000, 1, 1),
            gender='M',
            custodian=self.custodian
        )

    def test_subject_creation(self):
        """Test that a subject can be created"""
        self.assertEqual(self.subject.name, 'Test Subject')
        self.assertEqual(self.subject.custodian, self.custodian)
        self.assertTrue(self.subject.is_active)

    def test_subject_str(self):
        """Test the string representation of a subject"""
        expected = f"{self.subject.name} (Custodian: {self.custodian})"
        self.assertEqual(str(self.subject), expected)

class SubjectQRTests(TestCase):
    def setUp(self):
        # Create test user and custodian
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.custodian = self.user.custodian
        
        # Create test subject
        self.subject = Subject.objects.create(
            name='Test Subject',
            date_of_birth=date(2000, 1, 1),
            gender='M',
            custodian=self.custodian
        )
        
        # Create test QR code
        self.qr = SubjectQR.objects.create(
            subject=self.subject,
            is_active=True
        )

    def test_qr_creation(self):
        """Test that a QR code can be created"""
        self.assertEqual(self.qr.subject, self.subject)
        self.assertTrue(self.qr.is_active)
        self.assertIsNotNone(self.qr.uuid)

    def test_qr_activation(self):
        """Test QR code activation"""
        # Create another QR code
        qr2 = SubjectQR.objects.create(
            subject=self.subject,
            is_active=False
        )
        
        # Activate the second QR code
        qr2.is_active = True
        qr2.save()
        
        # Check that the first QR code is deactivated
        self.qr.refresh_from_db()
        self.assertFalse(self.qr.is_active)
        self.assertTrue(qr2.is_active)

class AlarmTests(TestCase):
    def setUp(self):
        # Create test user and custodian
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.custodian = self.user.custodian
        
        # Create test subject
        self.subject = Subject.objects.create(
            name='Test Subject',
            date_of_birth=date(2000, 1, 1),
            gender='M',
            custodian=self.custodian
        )
        
        # Create test QR code
        self.qr = SubjectQR.objects.create(
            subject=self.subject,
            is_active=True
        )
        
        # Create test alarm
        self.alarm = Alarm.objects.create(
            subject=self.subject,
            qr_code=self.qr,
            location='Test Location'
        )

    def test_alarm_creation(self):
        """Test that an alarm can be created"""
        self.assertEqual(self.alarm.subject, self.subject)
        self.assertEqual(self.alarm.qr_code, self.qr)
        self.assertEqual(self.alarm.location, 'Test Location')
        self.assertFalse(self.alarm.notification_sent)
        self.assertIsNotNone(self.alarm.timestamp)

    def test_alarm_str(self):
        """Test the string representation of an alarm"""
        expected = f"Alarm for {self.subject.name} at {self.alarm.timestamp}"
        self.assertEqual(str(self.alarm), expected)
