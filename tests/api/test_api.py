import os
import sys
import django
from django.conf import settings

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import json
import time
from django.test import Client
from django.contrib.auth.models import User

# Create a test client
client = Client()

def test_login():
    print("\n=== Testing Login ===")
    try:
        # Get CSRF token
        response = client.get('/login/')
        csrf_token = client.cookies['csrftoken'].value
        
        data = {
            'csrfmiddlewaretoken': csrf_token,
            'username': 'testadmin',
            'password': 'Str0ngP@ssw0rd123!'
        }
        response = client.post('/login/', data=data, follow=True)
        print(f"Login Status: {response.status_code}")
        
        # Verify we are logged in
        if not client.session.get('_auth_user_id'):
            print("No session found after login")
            return False
            
        print("Successfully logged in")
        return True
    except Exception as e:
        print(f"Login error: {str(e)}")
        return False

def test_subject_api():
    print("\n=== Testing Subject API ===")
    try:
        # Create subject
        data = {
            'name': 'Test Subject',
            'date_of_birth': '2000-01-01',
            'gender': 'M',
            'medical_conditions': 'None',
            'allergies': 'None',
            'medications': 'None'
        }
        response = client.post(
            '/api/v1/subjects/',
            data=json.dumps(data),
            content_type='application/json'
        )
        print(f"Create Subject Status: {response.status_code}")
        print(f"Response: {response.content.decode()}")
        
        # List subjects
        response = client.get('/api/v1/subjects/')
        print(f"List Subjects Status: {response.status_code}")
        print(f"Response: {response.content.decode()}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Subject API error: {str(e)}")
        return False

def test_alarm_api():
    print("\n=== Testing Alarm API ===")
    try:
        # Get first subject for the alarm
        response = client.get('/api/v1/subjects/')
        if response.status_code != 200:
            print("Failed to get subjects for alarm creation")
            return False
            
        subjects = json.loads(response.content.decode())
        if not subjects:
            print("No subjects found for alarm creation")
            return False
        
        subject_id = subjects[0]['id']
        
        # Create alarm
        data = {
            'subject': subject_id,
            'location': 'Test Location'
        }
        response = client.post(
            '/api/v1/alarms/',
            data=json.dumps(data),
            content_type='application/json'
        )
        print(f"Create Alarm Status: {response.status_code}")
        print(f"Response: {response.content.decode()}")
        
        # List alarms
        response = client.get('/api/v1/alarms/')
        print(f"List Alarms Status: {response.status_code}")
        print(f"Response: {response.content.decode()}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Alarm API error: {str(e)}")
        return False

def test_qr_code():
    print("\n=== Testing QR Code Generation ===")
    try:
        # Get first subject ID
        response = client.get('/api/v1/subjects/')
        if response.status_code != 200:
            print("Failed to get subjects")
            return False
            
        subjects = json.loads(response.content.decode())
        if not subjects:
            print("No subjects found")
            return False
        
        subject_id = subjects[0]['id']
        
        # Generate QR code
        data = {
            'subject_id': subject_id,
            'activate': 'on'
        }
        response = client.post('/subjects/qr/generate/', data=data)
        print(f"QR Code Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.content.decode()}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"QR Code error: {str(e)}")
        return False

def main():
    success = True
    
    # Test login
    success &= test_login()
    time.sleep(1)
    
    # Test APIs
    success &= test_subject_api()
    time.sleep(1)
    success &= test_alarm_api()
    time.sleep(1)
    success &= test_qr_code()
    
    print("\n=== Test Summary ===")
    print("All tests passed!" if success else "Some tests failed!")

if __name__ == "__main__":
    main() 