import os
import sys
import django
from django.conf import settings
import pytest
import json
import uuid
from datetime import datetime, date

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from custodians.models import Custodian
from subjects.models import Subject, SubjectQR
from alarms.models import Alarm

# Test Data
TEST_USER = {
    'username': 'testuser',
    'password': 'testpass123',
    'email': 'test@example.com'
}

TEST_CUSTODIAN = {
    'phone_number': '+1234567890',
    'address': 'Test Address',
    'is_verified': True
}

TEST_SUBJECT = {
            'name': 'Test Subject',
            'date_of_birth': '2000-01-01',
            'gender': 'M',
            'medical_conditions': 'None',
            'allergies': 'None',
            'medications': 'None'
        }

@pytest.fixture
def auth_headers(auth_client):
    """Get authentication headers"""
    # Make a GET request first to get the CSRF token
    response = auth_client.get('/api/v1/subjects/')  # Any GET request will do
    csrf_token = auth_client.cookies.get('csrftoken')
    if not csrf_token:
        from django.middleware.csrf import get_token
        csrf_token = get_token(response.wsgi_request)
    return {
        'HTTP_X_CSRFTOKEN': csrf_token,
        'content_type': 'application/json'
    }

@pytest.fixture
def test_custodian(auth_client, django_user_model):
    """Create a test custodian"""
    user = django_user_model.objects.get(username=TEST_USER['username'])
    custodian = user.custodian
    for field, value in TEST_CUSTODIAN.items():
        setattr(custodian, field, value)
    custodian.save()
    return custodian

@pytest.fixture
def test_subject(test_custodian):
    """Create a test subject"""
    subject = Subject.objects.create(
        custodian=test_custodian,
        **TEST_SUBJECT
    )
    return subject

@pytest.mark.django_db
class TestSubjectAPI:
    """Test Subject API endpoints"""
    
    def test_list_subjects(self, auth_client, test_subject):
        """Test GET /api/v1/subjects/"""
        response = auth_client.get('/api/v1/subjects/')
        assert response.status_code == 200
        data = json.loads(response.content)
        assert len(data) > 0
        # Find the test subject in the response data
        test_subject_data = next((item for item in data if item['id'] == test_subject.id), None)
        assert test_subject_data is not None
        assert test_subject_data['name'] == TEST_SUBJECT['name']

    def test_create_subject(self, auth_client, test_custodian, auth_headers):
        """Test POST /api/v1/subjects/"""
        new_subject = {
            **TEST_SUBJECT,
            'name': 'New Test Subject',
            'custodian': test_custodian.id
        }
        response = auth_client.post(
            '/api/v1/subjects/',
            data=json.dumps(new_subject),
            **auth_headers
        )
        assert response.status_code == 201
        data = json.loads(response.content)
        assert data['name'] == 'New Test Subject'

    def test_get_subject(self, auth_client, test_subject):
        """Test GET /api/v1/subjects/<id>/"""
        response = auth_client.get(f'/api/v1/subjects/{test_subject.id}/')
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['name'] == TEST_SUBJECT['name']

    def test_update_subject(self, auth_client, test_subject, auth_headers):
        """Test PUT /api/v1/subjects/<id>/"""
        updated_data = {
            **TEST_SUBJECT,
            'name': 'Updated Subject'
        }
        response = auth_client.put(
            f'/api/v1/subjects/{test_subject.id}/',
            data=json.dumps(updated_data),
            **auth_headers
        )
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['name'] == 'Updated Subject'

    def test_delete_subject(self, auth_client, test_subject):
        """Test DELETE /api/v1/subjects/<id>/"""
        response = auth_client.delete(f'/api/v1/subjects/{test_subject.id}/')
        assert response.status_code == 204

@pytest.mark.django_db
class TestQRCodeAPI:
    """Test QR Code endpoints"""
    
    def test_generate_qr(self, auth_client, test_subject):
        """Test POST /subjects/qr/generate/"""
        data = {
            'subject_id': test_subject.id,
            'activate': 'on'
        }
        response = auth_client.post('/subjects/qr/generate/', data=data)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert 'uuid' in data
        assert data['success'] is True

    def test_qr_operations(self, auth_client, test_subject):
        """Test QR code activation/deactivation"""
        # Generate QR
        qr = SubjectQR.objects.create(
            subject=test_subject,
            uuid=str(uuid.uuid4()),
            is_active=True
        )
        
        # Test deactivate
        response = auth_client.post(f'/subjects/qr/{qr.uuid}/deactivate/')
        assert response.status_code == 200
        qr.refresh_from_db()
        assert not qr.is_active

        # Test activate
        response = auth_client.post(f'/subjects/qr/{qr.uuid}/activate/')
        assert response.status_code == 200
        qr.refresh_from_db()
        assert qr.is_active

    def test_trigger_alarm(self, auth_client, test_subject):
        """Test POST /subjects/qr/<uuid>/trigger/"""
        qr = SubjectQR.objects.create(
            subject=test_subject,
            uuid=str(uuid.uuid4()),
            is_active=True
        )
        
        data = {
            'lat': '20.123',
            'lng': '-100.456'
        }
        response = auth_client.post(
            f'/subjects/qr/{qr.uuid}/trigger/', 
            data=data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['status'] == 'success'

@pytest.mark.django_db
class TestAlarmAPI:
    """Test Alarm API endpoints"""
    
    def test_list_alarms(self, auth_client, test_subject):
        """Test GET /api/v1/alarms/"""
        # Create test alarm
        Alarm.objects.create(subject=test_subject)
        
        response = auth_client.get('/api/v1/alarms/')
        assert response.status_code == 200
        data = json.loads(response.content)
        assert len(data) > 0

    def test_create_alarm(self, auth_client, test_subject, auth_headers):
        """Test POST /api/v1/alarms/"""
        data = {
            'subject': test_subject.id,
            'location': '20.123,-100.456'
        }
        response = auth_client.post(
            '/api/v1/alarms/',
            data=json.dumps(data),
            **auth_headers
        )
        assert response.status_code == 201
        data = json.loads(response.content)
        assert data['subject'] == test_subject.id

    def test_get_alarm(self, auth_client, test_subject):
        """Test GET /api/v1/alarms/<id>/"""
        alarm = Alarm.objects.create(subject=test_subject)
        
        response = auth_client.get(f'/api/v1/alarms/{alarm.id}/')
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['subject'] == test_subject.id

    def test_retry_notification(self, auth_client, test_subject):
        """Test POST /alarms/<id>/retry-notification/"""
        alarm = Alarm.objects.create(
            subject=test_subject,
            notification_sent=False
        )
        
        response = auth_client.post(f'/alarms/{alarm.id}/retry-notification/')
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True

    def test_alarm_statistics(self, auth_client):
        """Test GET /alarms/statistics/data/"""
        response = auth_client.get('/alarms/statistics/data/')
        assert response.status_code == 200
        data = json.loads(response.content)
        assert 'total_alarms' in data
        assert 'notifications' in data

@pytest.mark.django_db
class TestExportAPI:
    """Test Export endpoints"""
    
    def test_export_csv(self, auth_client):
        """Test GET /alarms/export/csv/"""
        response = auth_client.get('/alarms/export/csv/')
        assert response.status_code == 200
        assert response['Content-Type'] == 'text/csv'

    def test_export_excel(self, auth_client):
        """Test GET /alarms/export/excel/"""
        response = auth_client.get('/alarms/export/excel/')
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    def test_export_pdf(self, auth_client):
        """Test GET /alarms/export/pdf/"""
        response = auth_client.get('/alarms/export/pdf/')
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/pdf' 