# Alarm System

## Overview
The Alarm System is a critical component of Keryu that handles emergency notifications and tracking of Yus through Ker scans. It provides real-time alerts to custodians and emergency contacts when a Yu's Ker is scanned.

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

The Alarm model represents emergency notifications triggered by Ker scans. Each alarm contains:

#### Core Fields
- `subject`: ForeignKey to Subject model
- `qr_code`: ForeignKey to QRCode model
- `timestamp`: DateTime of alarm creation
- `location`: CharField(255) for scan location
- `description`: TextField for situation details
- `is_active`: Boolean indicating if alarm is active

#### Situation Types
- `situation_type`: CharField with choices:
  - TEST: System testing alarm
  - INJURED: Subject injury report
  - LOST: Missing subject report
  - CONTACT: Contact request alarm
- `is_test`: Boolean derived from situation_type

#### Scanner Information
- `is_phototaker`: Boolean indicating if scan from Phototaker app
- `scanner_ip`: IPAddressField for scanner's IP
- `scanner_user_agent`: TextField for scanner's user agent
- `scanner_location`: Point field for GPS coordinates

#### Notification Tracking
- `notification_sent`: Boolean for notification status
- `notification_timestamp`: DateTime of last notification
- `notification_attempts`: Integer count of send attempts
- `notification_status`: CharField for current status

```python
class Alarm(models.Model):
    """Model for tracking alarms triggered by QR code scans."""
    subject = models.ForeignKey('subjects.Subject', on_delete=models.CASCADE, related_name='alarms')
    qr_code = models.ForeignKey('subjects.SubjectQR', on_delete=models.SET_NULL, null=True, related_name='alarms')
    timestamp = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    is_test = models.BooleanField(default=False)
    scanned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    # Situation details
    SITUATION_TYPES = [
        ('TEST', 'Test Scan'),
        ('INJURED', 'Subject Injured'),
        ('LOST', 'Subject Lost'),
        ('CONTACT', 'Subject Needs Contact')
    ]
    situation_type = models.CharField(max_length=20, choices=SITUATION_TYPES, default='TEST')
    description = models.TextField(null=True, blank=True)
    
    # Scanner details
    is_phototaker = models.BooleanField(default=False)
    scanner_ip = models.GenericIPAddressField(null=True, blank=True)
    scanner_user_agent = models.TextField(blank=True)
    
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
            models.Index(fields=['situation_type'], name='alarms_situation_type_idx'),
            models.Index(fields=['is_phototaker'], name='alarms_is_phototaker_idx'),
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
   - Ker scan trigger
   - Location tracking
   - Timestamp recording
   - Scanner identification (Phototaker or web)
   - Situation type selection
   - Description capture
   - Test mode support

2. **Scanner Types**
   - Phototaker app users
     * Mobile-optimized form
     * Situation selection
     * Location capture
     * Description input
   - Regular web users
     * Standard form
     * Test scan support
     * Anonymous access

3. **Issue Tracking**
   - Issue type categorization
   - Detailed description
   - Location information
   - Timestamp tracking

4. **Resolution Management**
   - Resolution timestamp
   - Resolution notes
   - Resolution status tracking
   - Resolution workflow

5. **Notification System**
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

## Message Templates

### WhatsApp Notification Templates
Messages are formatted based on situation type:

#### Test Alarm
```
🔔 TEST ALARM
Yu: {subject_name}
Location: {location}
Time: {timestamp}
```

#### Injury Report
```
⚠️ INJURY REPORTED
Yu: {subject_name}
Location: {location}
Details: {description}
Time: {timestamp}
```

#### Lost Subject
```
🚨 YU MISSING
Yu: {subject_name}
Last Seen: {location}
Details: {description}
Time: {timestamp}
```

#### Contact Request
```
📞 CONTACT NEEDED
Yu: {subject_name}
Location: {location}
Message: {description}
Time: {timestamp}
```

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