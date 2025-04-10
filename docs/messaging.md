# Messaging System

## Overview
The Messaging System is a core component of Keryu that handles communication across multiple channels (WhatsApp, Email, SMS) for notifications and alerts. It provides a unified interface for sending messages while managing channel-specific requirements and limitations.

## Models

### Message Model
```python
class Message(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed')
    ]

    CHANNEL_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
        ('sms', 'SMS')
    ]

    recipient = models.ForeignKey('custodians.Custodian', on_delete=models.CASCADE)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    content = models.TextField()
    template_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
```

### MessageTemplate Model
```python
class MessageTemplate(models.Model):
    CHANNEL_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
        ('sms', 'SMS')
    ]

    name = models.CharField(max_length=100)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    content = models.TextField()
    variables = models.JSONField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## Features

### Message Management
1. **Creation**
   - Channel selection
   - Content formatting
   - Template support
   - Variable substitution

2. **Delivery**
   - Queue management
   - Channel routing
   - Status tracking
   - Error handling

3. **Templates**
   - Variable support
   - Channel-specific formatting
   - Version control
   - Active/Inactive status

### Channel Support

#### WhatsApp
1. **Configuration**
   - API credentials
   - Template management
   - Rate limits
   - Error handling

2. **Features**
   - Template messages
   - Media support
   - Interactive messages
   - Delivery receipts

#### Email
1. **Configuration**
   - SMTP settings
   - Template engine
   - Spam prevention
   - Bounce handling

2. **Features**
   - HTML templates
   - Attachments
   - Reply-to
   - Tracking

#### SMS
1. **Configuration**
   - Provider settings
   - Cost optimization
   - Character limits
   - Delivery tracking

2. **Features**
   - Unicode support
   - Long messages
   - Delivery reports
   - Cost tracking

## Tasks and Background Jobs

### Message Processing
1. **Queue Management**
   - Priority handling
   - Rate limiting
   - Channel balancing
   - Error recovery

2. **Delivery**
   - Channel routing
   - Status updates
   - Retry logic
   - Error logging

3. **Cleanup**
   - Old message cleanup
   - Failed message handling
   - Status updates
   - Database maintenance

### Monitoring
1. **System Health**
   - Channel status
   - Queue length
   - Error rates
   - Performance metrics

2. **Usage Statistics**
   - Message counts
   - Success rates
   - Channel usage
   - Cost tracking

## API Endpoints

### Message Management
- `GET /api/messages/` - List messages
- `POST /api/messages/` - Send message
- `GET /api/messages/{id}/` - Get message details
- `PUT /api/messages/{id}/` - Update message
- `DELETE /api/messages/{id}/` - Delete message

### Template Management
- `GET /api/templates/` - List templates
- `POST /api/templates/` - Create template
- `GET /api/templates/{id}/` - Get template details
- `PUT /api/templates/{id}/` - Update template
- `DELETE /api/templates/{id}/` - Delete template

## Views and Templates

### Message Views
1. **List View**
   - Status filtering
   - Channel filtering
   - Date filtering
   - Pagination

2. **Detail View**
   - Message content
   - Delivery status
   - Error details
   - Action buttons

3. **Dashboard**
   - Message statistics
   - Channel status
   - Recent messages
   - Quick actions

### Template Views
1. **Management**
   - Template list
   - Create/Edit form
   - Variable editor
   - Preview

2. **Usage**
   - Usage statistics
   - Success rates
   - Error logs
   - Version history

## Error Handling

### Processing Errors
1. **Channel Errors**
   - Connection issues
   - Rate limits
   - Invalid recipients
   - Message formatting

2. **System Errors**
   - Queue failures
   - Database errors
   - Cache errors
   - Resource limits

### Recovery Procedures
1. **Automatic Recovery**
   - Retry logic
   - Fallback channels
   - Error logging
   - Status updates

2. **Manual Intervention**
   - Error reporting
   - Manual retry
   - Channel switching
   - Resolution handling

## Best Practices

### Performance
1. **Optimization**
   - Queue management
   - Batch processing
   - Cache usage
   - Database indexing

2. **Monitoring**
   - Response times
   - Success rates
   - Error rates
   - Resource usage

### Security
1. **Access Control**
   - Permission checks
   - Rate limiting
   - Input validation
   - Audit logging

2. **Data Protection**
   - Encryption
   - Secure storage
   - Access logs
   - Compliance

## Testing

### Unit Tests
- Model tests
- Service tests
- Template tests
- Utility tests

### Integration Tests
- API tests
- Channel tests
- Queue tests
- Database tests

### Manual Testing
- UI testing
- Channel testing
- Template testing
- Error scenarios 