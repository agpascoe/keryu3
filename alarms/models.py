from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError

class NotificationStatus:
    PENDING = 'PENDING'
    PROCESSING = 'PROCESSING'
    ACCEPTED = 'ACCEPTED'  # Message accepted by service
    SENT = 'SENT'         # Message sent by service
    DELIVERED = 'DELIVERED'  # Message delivered to device
    FAILED = 'FAILED'
    ERROR = 'ERROR'

    CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (ACCEPTED, 'Accepted'),
        (SENT, 'Sent'),
        (DELIVERED, 'Delivered'),
        (FAILED, 'Failed'),
        (ERROR, 'Error'),
    ]

class NotificationChannel:
    WHATSAPP = 'whatsapp'
    EMAIL = 'email'
    SMS = 'sms'

    CHOICES = [
        (WHATSAPP, 'WhatsApp'),
        (EMAIL, 'Email'),
        (SMS, 'SMS'),
    ]

class Alarm(models.Model):
    """Model for tracking alarms triggered by QR code scans."""
    SITUATION_TYPES = [
        ('INJURED', 'Yu Injured'),
        ('LOST', 'Yu Lost'),
        ('CONTACT', 'Yu Requesting Contact')
    ]

    subject = models.ForeignKey('subjects.Subject', on_delete=models.CASCADE, related_name='alarms')
    qr_code = models.ForeignKey('subjects.SubjectQR', on_delete=models.SET_NULL, null=True, related_name='alarms')
    timestamp = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255, default='')
    is_test = models.BooleanField(default=False)
    scanned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    # Issue details
    situation_type = models.CharField(
        max_length=20,
        choices=SITUATION_TYPES,
        null=True,
        blank=True
    )
    description = models.TextField(null=True, blank=True)
    is_anonymous = models.BooleanField(default=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)  # For tracking device info
    
    # Resolution fields
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    # Notification tracking fields
    notification_sent = models.BooleanField(default=False)
    notification_error = models.TextField(blank=True, null=True)
    notification_attempt_count = models.IntegerField(default=0)
    last_attempt = models.DateTimeField(null=True, blank=True)
    message_sid = models.CharField(max_length=50, blank=True, null=True)  # Store Twilio message SID
    whatsapp_message_id = models.CharField(max_length=100, blank=True, null=True)  # Store WhatsApp message ID
    notification_status = models.CharField(
        max_length=20,
        choices=NotificationStatus.CHOICES,
        default=NotificationStatus.PENDING
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Alarm'
        verbose_name_plural = 'Alarms'
        indexes = [
            models.Index(fields=['timestamp'], name='alarms_timestamp_idx'),
            models.Index(fields=['notification_status'], name='alarms_status_idx'),
            models.Index(fields=['subject', 'timestamp'], name='alarms_subject_timestamp_idx'),
            models.Index(fields=['resolved_at'], name='alarms_resolved_at_idx'),
            models.Index(fields=['situation_type'], name='alarms_situation_type_idx'),
        ]

    def __str__(self):
        return f"Alarm for {self.subject.name} at {self.timestamp}"

    def resolve(self, notes=""):
        """Mark the alarm as resolved with optional notes."""
        self.resolved_at = timezone.now()
        self.resolution_notes = notes
        self.save()

class NotificationAttempt(models.Model):
    """Model for tracking individual notification attempts."""
    MAX_RETRIES = 3
    
    alarm = models.ForeignKey(
        Alarm,
        on_delete=models.CASCADE,
        related_name='notification_attempts'
    )
    recipient = models.ForeignKey('custodians.Custodian', on_delete=models.CASCADE)
    channel = models.CharField(max_length=20, choices=NotificationChannel.CHOICES)
    status = models.CharField(max_length=20, choices=NotificationStatus.CHOICES, default=NotificationStatus.PENDING)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    retry_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['alarm', 'channel'], name='notif_alarm_channel_idx'),
            models.Index(fields=['status'], name='notif_status_idx'),
            models.Index(fields=['created_at'], name='notif_created_at_idx'),
        ]
    
    def mark_sent(self):
        """Mark the notification attempt as sent."""
        self.status = NotificationStatus.SENT
        self.sent_at = timezone.now()
        self.save(update_fields=['status', 'sent_at'])
        
        # Update alarm status
        self.alarm.notification_sent = True
        self.alarm.notification_status = NotificationStatus.SENT
        self.alarm.save(update_fields=['notification_sent', 'notification_status'])
    
    def mark_failed(self, error_message):
        """Mark the notification attempt as failed."""
        if self.status == NotificationStatus.SENT:
            raise ValidationError("Cannot mark a sent notification as failed")
            
        self.status = NotificationStatus.FAILED
        self.error_message = error_message
        self.retry_count += 1
        self.save()
        
        # Update alarm status if max retries reached
        if self.retry_count >= self.MAX_RETRIES:
            self.alarm.notification_status = NotificationStatus.FAILED
            self.alarm.save()

    def save(self, *args, **kwargs):
        """Override save to update alarm's notification attempt count."""
        is_new = self._state.adding
        super().save(*args, **kwargs)
        
        if is_new:
            # Update alarm's notification attempt count
            self.alarm.notification_attempt_count = (
                NotificationAttempt.objects.filter(alarm=self.alarm).count()
            )
            self.alarm.save()
