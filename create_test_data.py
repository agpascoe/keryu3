from django.contrib.auth.models import User
from custodians.models import Custodian
from subjects.models import Subject, SubjectQR, Alarm
from django.utils import timezone
from datetime import datetime

def create_test_data():
    # Create test user
    user = User.objects.create_user(
        username='testuser',
        password='testpass123',
        email='test@example.com'
    )

    # Create test custodian
    custodian = Custodian.objects.create(
        user=user,
        phone_number='+1234567890',
        address='123 Test St',
        is_verified=True
    )

    # Create test subject
    subject = Subject.objects.create(
        name='Test Subject',
        date_of_birth=datetime(1990, 1, 1),
        gender='M',
        custodian=custodian,
        doctor_name='Dr. Test',
        doctor_phone='+1234567890',
        medical_conditions='Test condition'
    )

    # Create QR code for subject
    qr_code = SubjectQR.objects.create(
        subject=subject,
        activation_method='manual',
        is_active=True
    )

    # Create test alarm
    alarm = Alarm.objects.create(
        subject=subject,
        qr_code=qr_code,
        timestamp=timezone.now(),
        notification_sent=False
    )

    print("Test data created successfully!")
    print(f"Subject ID: {subject.id}")
    print(f"QR Code ID: {qr_code.id}")
    print(f"Alarm ID: {alarm.id}")
    print(f"Test user created with username: testuser and password: testpass123")

if __name__ == '__main__':
    create_test_data() 