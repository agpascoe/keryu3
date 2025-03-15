from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from custodians.models import Custodian
from subjects.models import Subject, SubjectQR
from phonenumber_field.phonenumber import PhoneNumber

class Command(BaseCommand):
    help = 'Creates test data for QR code testing'

    def handle(self, *args, **options):
        # Create test user and custodian
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS('Created test user'))

        # Update or create custodian
        custodian, created = Custodian.objects.update_or_create(
            user=user,
            defaults={
                'phone_number': PhoneNumber.from_string('+5215555555555'),
                'is_verified': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created test custodian'))

        # Create test subject
        subject, created = Subject.objects.get_or_create(
            name='Test Subject',
            custodian=custodian,
            defaults={
                'date_of_birth': '2000-01-01',
                'gender': 'O',
                'medical_conditions': 'None',
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created test subject'))

        # Create and activate QR code
        qr_code, created = SubjectQR.objects.get_or_create(
            subject=subject,
            defaults={
                'is_active': True,
                'activated_at': timezone.now()
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created test QR code'))
        
        self.stdout.write(self.style.SUCCESS(f'Test QR code UUID: {qr_code.uuid}')) 