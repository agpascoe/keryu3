from django.db import models
from django.utils import timezone
import uuid
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.

class Subject(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]

    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    medical_conditions = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    medications = models.TextField(blank=True)
    custodian = models.ForeignKey('custodians.Custodian', on_delete=models.CASCADE, related_name='subjects')
    doctor_name = models.CharField(max_length=100, blank=True, help_text='Primary care physician')
    doctor_phone = PhoneNumberField(blank=True, null=True, help_text='Doctor\'s contact number')
    doctor_address = models.TextField(blank=True, help_text='Doctor\'s office address')
    doctor_speciality = models.CharField(max_length=100, blank=True, help_text='Doctor\'s speciality')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    photo = models.ImageField(upload_to='subject_photos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} (Custodian: {self.custodian})"

    class Meta:
        ordering = ['name']

class SubjectQR(models.Model):
    """Model for managing QR codes associated with subjects."""
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='qr_codes')
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    last_used = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    image = models.ImageField(upload_to='qr_codes/', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'QR Code'
        verbose_name_plural = 'QR Codes'

    def __str__(self):
        return f"QR Code for {self.subject.name} ({self.uuid})"

    def save(self, *args, **kwargs):
        if self.is_active:
            if not self.activated_at:
                self.activated_at = timezone.now()
            # Deactivate other QR codes for this subject
            SubjectQR.objects.filter(subject=self.subject).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

class Alarm(models.Model):
    """Model for tracking alarms triggered by QR code scans."""
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='alarms')
    qr_code = models.ForeignKey(SubjectQR, on_delete=models.SET_NULL, null=True, related_name='alarms')
    timestamp = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    
    # Notification tracking fields
    notification_sent = models.BooleanField(default=False)
    notification_error = models.TextField(null=True, blank=True)
    notification_attempts = models.IntegerField(default=0)
    last_attempt = models.DateTimeField(null=True, blank=True)
    whatsapp_message_id = models.CharField(max_length=255, null=True, blank=True)
    notification_status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('SENT', 'Sent'),
            ('DELIVERED', 'Delivered'),
            ('FAILED', 'Failed'),
            ('ERROR', 'Error'),
        ],
        default='PENDING'
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Alarm'
        verbose_name_plural = 'Alarms'

    def __str__(self):
        return f"Alarm for {self.subject.name} at {self.timestamp}"
