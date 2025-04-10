# Alarm System

## Overview
The Alarm System is a critical component of Keryu that handles emergency notifications and tracking of subjects through QR code scans. It provides real-time alerts to custodians and emergency contacts when a subject's QR code is scanned.

## Models

### NotificationStatus
```python
class NotificationStatus:
    PENDING = 'PENDING'
    PROCESSING = 'PROCESSING'
    SENT = 'SENT'
    DELIVERED = 'DELIVERED'
    FAILED = 'FAILED'
    ERROR = 'ERROR'

    CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (SENT, 'Sent'),
        (DELIVERED, 'Delivered'),
        (FAILED, 'Failed'),
        (ERROR, 'Error'),
    ]
```

### NotificationChannel
```python
class NotificationChannel:
    WHATSAPP = 'whatsapp'
    EMAIL = 'email'
    SMS = 'sms'

    CHOICES = [
        (WHATSAPP, 'WhatsApp'),
        (EMAIL, 'Email'),
        (SMS, 'SMS'),
    ]
```

### Alarm Model
```python
class Alarm(models.Model):
    """Model for tracking alarms triggered by QR code scans."""
    subject = models.ForeignKey('subjects.Subject', on_delete=models.CASCADE, related_name='alarms')
    qr_code = models.ForeignKey('subjects.SubjectQR', on_delete=models.SET_NULL, null=True, related_name='alarms')
    timestamp = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    is_test = models.BooleanField(default=False)
    scanned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    # Issue details
    issue_type = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    
    # Resolution fields
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    # Notification tracking fields
    notification_sent = models.BooleanField(default=False)
    notification_error = models.TextField(null=True, blank=True)
    notification_attempts = models.IntegerField(default=0)
    last_attempt = models.DateTimeField(null=True, blank=True)
    whatsapp_message_id = models.CharField(max_length=255, null=True, blank=True)
    notification_status = models.CharField(
        max_length=20,
        choices=NotificationStatus.CHOICES,
        default=NotificationStatus.PENDING
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
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
        ]
```

### NotificationAttempt Model
```python
class NotificationAttempt(models.Model):
    """Model for tracking individual notification attempts."""
    alarm = models.ForeignKey(Alarm, on_delete=models.CASCADE, related_name='notification_attempts')
    recipient = models.ForeignKey('custodians.Custodian', on_delete=models.CASCADE)
    channel = models.CharField(max_length=20, choices=NotificationChannel.CHOICES)
    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.CHOICES,
        default=NotificationStatus.PENDING
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Notification Attempt'
        verbose_name_plural = 'Notification Attempts'
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['alarm', 'channel'], name='notification_attempts_alarm_channel_idx'),
            models.Index(fields=['status'], name='notification_attempts_status_idx'),
        ]
```

## Features

### Alarm Management
1. **Creation**
   - QR code scan trigger
   - Location tracking
   - Timestamp recording
   - Scanner identification
   - Test mode support

2. **Issue Tracking**
   - Issue type categorization
   - Detailed description
   - Location information
   - Timestamp tracking

3. **Resolution Management**
   - Resolution timestamp
   - Resolution notes
   - Resolution status tracking
   - Resolution workflow

4. **Notification System**
   - Multi-channel support (WhatsApp, Email, SMS)
   - Status tracking
   - Retry mechanism
   - Error handling

### Notification Processing
1. **Status Flow**
   - Pending → Processing → Sent → Delivered
   - Error handling with FAILED and ERROR states
   - Retry tracking with attempt counting
   - Channel-specific tracking

2. **Error Handling**
   - Error message storage
   - Attempt counting
   - Last attempt timestamp
   - Status tracking

3. **Channel Management**
   - WhatsApp integration
   - Email support
   - SMS capability
   - Channel-specific error handling

## API Endpoints

### Alarm Management
- `GET /api/alarms/` - List alarms
- `POST /api/alarms/` - Create alarm
- `GET /api/alarms/{id}/` - Get alarm details
- `DELETE /api/alarms/{id}/` - Delete alarm (staff only)
- `POST /api/alarms/{id}/resolve/` - Resolve alarm
- `GET /api/alarms/{id}/notification-attempts/` - List notification attempts

### Notification Management
- `POST /api/alarms/{id}/retry-notification/` - Retry failed notification
- `GET /api/alarms/statistics/` - Get alarm statistics
- `GET /api/notification-attempts/` - List all notification attempts

## Views and Templates

### Alarm Views
1. **List View**
   - Status filtering
   - Date filtering
   - Subject filtering
   - Resolution status
   - Pagination

2. **Detail View**
   - Alarm information
   - Notification status
   - Error details
   - Resolution form
   - Notification history
   - Retry options

3. **Dashboard**
   - Active alarms
   - Recent notifications
   - Statistics
   - Quick actions

### Notification Views
1. **History**
   - Channel breakdown
   - Success rates
   - Error logs
   - Retry attempts

2. **Management**
   - Channel settings
   - Template management
   - Rate limits
   - Cost tracking

## Error Handling

### Processing Errors
1. **Notification Errors**
   - Channel-specific issues
   - Message delivery failures
   - Rate limiting
   - Invalid recipients

2. **System Errors**
   - Database errors
   - Queue failures
   - Resource limits
   - Network issues

### Recovery Procedures
1. **Automatic Recovery**
   - Retry mechanism
   - Status updates
   - Error logging
   - Attempt tracking

2. **Manual Intervention**
   - Manual retry option
   - Error reporting
   - Status updates
   - Resolution handling

## Best Practices

### Performance
1. **Optimization**
   - Database indexing
   - Query optimization
   - Cache usage
   - Batch processing

2. **Monitoring**
   - Status tracking
   - Error rates
   - Success rates
   - Response times

### Security
1. **Access Control**
   - Permission checks
   - Rate limiting
   - Input validation
   - Audit logging

2. **Data Protection**
   - Secure storage
   - Access logs
   - Compliance
   - Privacy protection

## Testing

### Unit Tests
- Model tests
- Status transitions
- Notification tracking
- Resolution workflow
- Error handling

### Integration Tests
- API endpoints
- Channel integration
- Database operations
- Queue processing

### Manual Testing
- UI testing
- Notification flow
- Resolution workflow
- Error scenarios
- Recovery procedures 