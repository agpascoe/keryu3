# Messaging System Documentation

## Overview

The Keryu system supports multiple messaging channels for notifications:
1. Meta WhatsApp API (Primary)
2. Twilio WhatsApp (Fallback)
3. Twilio SMS (Fallback)

## System Architecture

### Service Dependencies
1. **Redis Server**
   - Message broker for Celery
   - Result backend for task status
   - Must be running before Celery services

2. **Celery Worker**
   - Processes messaging tasks
   - Handles retries and error cases
   - Uses solo pool for reliable processing
   - Listens to multiple queues:
     * alarms: Alarm and notification processing tasks
     * default: General tasks

3. **Celery Beat**
   - Schedules periodic tasks
   - Monitors message delivery status
   - Handles cleanup tasks

### Process Management
- All services managed via `startup.sh`
- Single instance enforcement
- Automatic cleanup of stale processes
- Health checks for all services

## Task Architecture

### Notification Tasks
The system uses a consolidated notification system with a single task:
```python
@app.task(bind=True, max_retries=3, name='alarms.tasks.send_whatsapp_notification')
def send_whatsapp_notification(self, alarm_id, is_test=False):
    """
    Send a WhatsApp notification for an alarm.
    Uses select_for_update to prevent race conditions.
    """
```

Key features:
- Transaction handling to prevent race conditions
- Status tracking with states: PENDING, PROCESSING, SENT, DELIVERED, FAILED, ERROR
- Maximum of 3 retry attempts
- Test mode support
- Duplicate notification prevention

### Status Tracking
The system tracks notification status using the following fields:
- notification_status: Current status of the notification
- notification_sent: Boolean indicating successful delivery
- notification_attempts: Number of delivery attempts
- last_attempt: Timestamp of the last attempt
- notification_error: Error message if delivery failed
- whatsapp_message_id: Message ID from the provider

## Channel Configuration

The system uses a dynamic channel selection mechanism through the `SystemParameter` model:
- Meta WhatsApp API (value: "1")
- Twilio WhatsApp (value: "2")
- Twilio SMS (value: "3")

### Setting the Channel

```python
from core.models import SystemParameter

# Set channel to Meta WhatsApp API
SystemParameter.objects.get_or_create(
    parameter="channel",
    defaults={"value": "1"}
)
```

## Phone Number Formatting

Each channel has specific phone number formatting requirements:

1. **Meta WhatsApp API**
   - Removes '+' prefix
   - Example: "+5212345678901" → "5212345678901"

2. **Twilio WhatsApp**
   - Adds 'whatsapp:' prefix
   - Formats Mexican numbers (adds '1' after '+52')
   - Example: "+5212345678901" → "whatsapp:+5212345678901"

3. **Twilio SMS**
   - Formats Mexican numbers (adds '1' after '+52')
   - Example: "+5212345678901" → "+5212345678901"

## Message Formatting

Messages are consistently formatted across all channels:
- Extra whitespace is removed
- Line breaks are converted to spaces
- Multiple spaces are reduced to single spaces

Example:
```python
"Hello   World\nTest   Message" → "Hello World Test Message"
```

## Error Handling

The system includes comprehensive error handling:
1. Channel-specific error handling
2. Automatic retries for failed messages (max 3 attempts)
3. Detailed error logging
4. Status tracking for message delivery
5. Race condition prevention using database locks

## Configuration

### Environment Variables

```env
# Meta WhatsApp API Configuration
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_ACCESS_TOKEN=your_access_token

# Twilio Configuration (Optional)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_phone_number
TWILIO_WHATSAPP_NUMBER=your_whatsapp_number

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### WhatsApp Template

The system uses a template named "qr_template_on_m" with two variables:
1. Subject name
2. Timestamp

## Testing

### QR Code Testing
The system provides direct URL access for QR code testing:
- Each QR code displays its corresponding scan URL
- URLs can be clicked directly to simulate QR code scanning
- Useful for testing the complete notification flow without physical QR codes
- Browser-native features (copy URL, open in new tab) are supported

### Automated Tests
Run the messaging tests:
```bash
python -m pytest tests/test_messaging.py -vv
```

The test suite covers:
1. Message formatting consistency
2. Phone number formatting
3. Channel selection
4. Error handling
5. Template message structure
6. QR code URL generation and scanning

## Monitoring

The system includes detailed logging for monitoring:
1. Message delivery status
2. API responses
3. Error tracking
4. Performance metrics
5. Celery task status
6. Worker health
7. Redis connection status

## Best Practices

1. **Phone Numbers**
   - Always use E.164 format
   - Include country code
   - Test with international numbers

2. **Messages**
   - Keep messages concise
   - Test with various character sets
   - Verify template compliance

3. **Error Handling**
   - Monitor error rates
   - Review failed deliveries
   - Adjust retry strategies

4. **Testing**
   - Run tests after configuration changes
   - Verify all channels
   - Test fallback scenarios
   - Use test mode for validation

5. **Process Management**
   - Use startup script for service management
   - Monitor worker processes
   - Check service logs regularly
   - Verify single instance operation 