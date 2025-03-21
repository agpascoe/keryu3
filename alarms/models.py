from django.db import models
from django.utils import timezone

class Alarm(models.Model):
    """Model for tracking alarms triggered by QR code scans."""
    subject = models.ForeignKey('subjects.Subject', on_delete=models.CASCADE, related_name='alarms_new')
    qr_code = models.ForeignKey('subjects.SubjectQR', on_delete=models.SET_NULL, null=True, related_name='alarms_new')
    timestamp = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    is_test = models.BooleanField(default=False)
    
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
            ('PROCESSING', 'Processing'),
            ('SENT', 'Sent'),
            ('DELIVERED', 'Delivered'),
            ('FAILED', 'Failed'),
            ('ERROR', 'Error'),
        ],
        default='PENDING'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Alarm'
        verbose_name_plural = 'Alarms'

    def __str__(self):
        return f"Alarm for {self.subject.name} at {self.timestamp}"
