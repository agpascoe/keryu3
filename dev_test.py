#!/usr/bin/env python
"""
Development test script for Keryu system.
This script provides various testing utilities for development.
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings_dev')
django.setup()

from django.contrib.auth.models import User
from custodians.models import Custodian
from subjects.models import Subject, SubjectQR
from alarms.models import Alarm
from notifications.providers import get_notification_service

def test_notification_system():
    """Test the notification system."""
    print("🧪 Testing Notification System...")
    
    # Get notification service
    service = get_notification_service()
    print(f"Using notification service: {service.name}")
    
    # Test message data
    test_data = {
        'subject_name': 'Test Subject',
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'location': 'Test Location'
    }
    
    # Send test message
    result = service.send_message('+1234567890', test_data)
    print(f"Notification result: {result}")
    
    return result['success']

def test_qr_code_generation():
    """Test QR code generation."""
    print("\n🧪 Testing QR Code Generation...")
    
    # Get or create a test subject
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User'}
    )
    
    custodian, created = Custodian.objects.get_or_create(
        user=user,
        defaults={'phone_number': '+1234567890'}
    )
    
    subject, created = Subject.objects.get_or_create(
        name='Test Subject',
        custodian=custodian,
        defaults={
            'date_of_birth': datetime.now().date() - timedelta(days=365*30),
            'gender': 'M',
            'medical_conditions': 'None',
            'allergies': 'None',
            'medications': 'None'
        }
    )
    
    print(f"Using subject: {subject.name}")
    
    # Generate QR code
    qr_code = SubjectQR.objects.create(subject=subject, is_active=True)
    print(f"Generated QR code: {qr_code.uuid}")
    print(f"QR code URL: http://localhost:8000/qr/{qr_code.uuid}/")
    
    return qr_code

def test_alarm_creation():
    """Test alarm creation."""
    print("\n🧪 Testing Alarm Creation...")
    
    # Get a subject
    subject = Subject.objects.first()
    if not subject:
        print("No subjects found. Creating test subject first...")
        test_qr_code_generation()
        subject = Subject.objects.first()
    
    # Create test alarm
    alarm = Alarm.objects.create(
        subject=subject,
        situation_type='TEST',
        description='This is a test alarm',
        is_anonymous=True,
        ip_address='127.0.0.1'
    )
    
    print(f"Created alarm: {alarm.id}")
    print(f"Alarm details: {alarm.subject.name} - {alarm.situation_type}")
    
    return alarm

def test_database_connection():
    """Test database connection and basic operations."""
    print("\n🧪 Testing Database Connection...")
    
    try:
        # Test basic queries
        user_count = User.objects.count()
        custodian_count = Custodian.objects.count()
        subject_count = Subject.objects.count()
        qr_count = SubjectQR.objects.count()
        alarm_count = Alarm.objects.count()
        
        print(f"Database connection successful!")
        print(f"Users: {user_count}")
        print(f"Custodians: {custodian_count}")
        print(f"Subjects: {subject_count}")
        print(f"QR Codes: {qr_count}")
        print(f"Alarms: {alarm_count}")
        
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

def create_test_data():
    """Create comprehensive test data."""
    print("\n🧪 Creating Test Data...")
    
    # Create test users
    users_data = [
        {'username': 'admin', 'email': 'admin@keryu.com', 'first_name': 'Admin', 'last_name': 'User'},
        {'username': 'custodian1', 'email': 'custodian1@keryu.com', 'first_name': 'John', 'last_name': 'Doe'},
        {'username': 'custodian2', 'email': 'custodian2@keryu.com', 'first_name': 'Jane', 'last_name': 'Smith'},
    ]
    
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults=user_data
        )
        if created:
            print(f"Created user: {user.username}")
    
    # Create custodians
    for user in User.objects.filter(is_superuser=False):
        custodian, created = Custodian.objects.get_or_create(
            user=user,
            defaults={'phone_number': f'+52{user.id}234567890'}
        )
        if created:
            print(f"Created custodian: {custodian}")
    
    # Create subjects
    subjects_data = [
        {'name': 'Alice Johnson', 'gender': 'F', 'medical_conditions': 'Asthma'},
        {'name': 'Bob Wilson', 'gender': 'M', 'medical_conditions': 'Diabetes'},
        {'name': 'Carol Brown', 'gender': 'F', 'medical_conditions': 'None'},
    ]
    
    for i, subject_data in enumerate(subjects_data):
        custodian = Custodian.objects.all()[i % Custodian.objects.count()]
        subject, created = Subject.objects.get_or_create(
            name=subject_data['name'],
            custodian=custodian,
            defaults={
                'date_of_birth': datetime.now().date() - timedelta(days=365*(20 + i*10)),
                'gender': subject_data['gender'],
                'medical_conditions': subject_data['medical_conditions'],
                'allergies': 'None',
                'medications': 'None'
            }
        )
        if created:
            print(f"Created subject: {subject.name}")
    
    print("Test data creation completed!")

def run_all_tests():
    """Run all development tests."""
    print("🚀 Starting Keryu Development Tests...")
    print("=" * 60)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Notification System", test_notification_system),
        ("QR Code Generation", test_qr_code_generation),
        ("Alarm Creation", test_alarm_creation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result, None))
        except Exception as e:
            results.append((test_name, False, str(e)))
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print("=" * 60)
    
    for test_name, success, error in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if error:
            print(f"   Error: {error}")
    
    print("=" * 60)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "test":
            run_all_tests()
        elif command == "create-data":
            create_test_data()
        elif command == "notification":
            test_notification_system()
        elif command == "qr":
            test_qr_code_generation()
        elif command == "alarm":
            test_alarm_creation()
        elif command == "db":
            test_database_connection()
        else:
            print("Unknown command. Available commands: test, create-data, notification, qr, alarm, db")
    else:
        run_all_tests() 