# API System

## Overview
The API System is a comprehensive component of Keryu that provides a RESTful interface for interacting with the application's core functionality. It implements secure, scalable, and well-documented endpoints for various system operations.

## Models

### APIToken Model
```python
class APIToken(models.Model):
    TOKEN_TYPES = [
        ('access', 'Access Token'),
        ('refresh', 'Refresh Token'),
        ('service', 'Service Token'),
    ]

    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    token_type = models.CharField(max_length=20, choices=TOKEN_TYPES)
    token = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
```

### APIRequest Model
```python
class APIRequest(models.Model):
    METHODS = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
        ('PATCH', 'PATCH'),
    ]

    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10, choices=METHODS)
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    request_data = models.JSONField()
    response_data = models.JSONField()
    status_code = models.IntegerField()
    duration = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
```

### APIRateLimit Model
```python
class APIRateLimit(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    endpoint = models.CharField(max_length=255)
    request_count = models.IntegerField(default=0)
    window_start = models.DateTimeField()
    window_end = models.DateTimeField()
    is_blocked = models.BooleanField(default=False)
    block_until = models.DateTimeField(null=True, blank=True)
```

## Features

### API Management
1. **Authentication**
   - Token-based auth
   - OAuth2 support
   - API key auth
   - Session auth

2. **Authorization**
   - Role-based access
   - Permission checks
   - Resource limits
   - Scope validation

3. **Rate Limiting**
   - Request limits
   - Time windows
   - Blocking rules
   - Exemption rules

### Request Handling
1. **Validation**
   - Input validation
   - Schema validation
   - Type checking
   - Format validation

2. **Processing**
   - Request parsing
   - Response formatting
   - Error handling
   - Logging

3. **Performance**
   - Caching
   - Compression
   - Pagination
   - Filtering

### Documentation
1. **API Documentation**
   - Endpoint docs
   - Request/response
   - Authentication
   - Examples

2. **Versioning**
   - Version control
   - Backward compatibility
   - Deprecation
   - Migration guides

## Tasks and Background Jobs

### Token Management
1. **Token Processing**
   - Token generation
   - Token validation
   - Token refresh
   - Token revocation

2. **Cleanup Tasks**
   - Expired token cleanup
   - Rate limit reset
   - Request log cleanup
   - Cache cleanup

### Monitoring
1. **Request Monitoring**
   - Usage tracking
   - Performance tracking
   - Error tracking
   - Rate limit tracking

2. **Analytics**
   - Usage patterns
   - Performance metrics
   - Error rates
   - User behavior

## API Endpoints

### Authentication
- `POST /api/v1/token/` - Get access token
  ```json
  Request:
  {
    "username": "string",
    "password": "string"
  }
  Response:
  {
    "access": "string",
    "refresh": "string"
  }
  ```
- `POST /api/v1/token/refresh/` - Refresh token
  ```json
  Request:
  {
    "refresh": "string"
  }
  Response:
  {
    "access": "string"
  }
  ```

### Users
- `GET /api/v1/users/` - List users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{id}/` - Get user
- `PUT /api/v1/users/{id}/` - Update user
- `DELETE /api/v1/users/{id}/` - Delete user

### Subjects
- `GET /api/v1/subjects/` - List subjects
  ```json
  Response:
  {
    "count": "integer",
    "results": [
      {
        "id": "integer",
        "name": "string",
        "date_of_birth": "date",
        "gender": "string",
        "medical_conditions": "string",
        "allergies": "string",
        "medications": "string",
        "custodian": "integer"
      }
    ]
  }
  ```
- `POST /api/v1/subjects/` - Create subject
- `GET /api/v1/subjects/{id}/` - Get subject
- `PUT /api/v1/subjects/{id}/` - Update subject
- `DELETE /api/v1/subjects/{id}/` - Delete subject

### Alarms
- `GET /api/v1/alarms/` - List alarms
  ```json
  Response:
  {
    "count": "integer",
    "results": [
      {
        "id": "integer",
        "subject": "integer",
        "qr_code": "integer",
        "timestamp": "datetime",
        "location": "string",
        "is_test": "boolean",
        "notification_status": "string",
        "notification_sent": "boolean",
        "notification_error": "string",
        "notification_attempt_count": "integer",
        "last_attempt": "datetime",
        "whatsapp_message_id": "string",
        "resolved_at": "datetime",
        "resolution_notes": "string",
        "created_at": "datetime",
        "updated_at": "datetime"
      }
    ]
  }
  ```
- `POST /api/v1/alarms/` - Create alarm
  ```json
  Request:
  {
    "subject": "integer",
    "qr_code": "integer",
    "location": "string",
    "is_test": "boolean"
  }
  Response:
  {
    "id": "integer",
    "subject": "integer",
    "qr_code": "integer",
    "location": "string",
    "is_test": "boolean",
    "notification_status": "PENDING",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
  ```
- `GET /api/v1/alarms/{id}/` - Get alarm details
  ```json
  Response:
  {
    "id": "integer",
    "subject": "integer",
    "qr_code": "integer",
    "timestamp": "datetime",
    "location": "string",
    "is_test": "boolean",
    "notification_status": "string",
    "notification_sent": "boolean",
    "notification_error": "string",
    "notification_attempt_count": "integer",
    "last_attempt": "datetime",
    "whatsapp_message_id": "string",
    "resolved_at": "datetime",
    "resolution_notes": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
  ```
- `PUT /api/v1/alarms/{id}/` - Update alarm
- `DELETE /api/v1/alarms/{id}/` - Delete alarm
- `POST /api/v1/alarms/{id}/resolve/` - Resolve alarm
  ```json
  Request:
  {
    "resolution_notes": "string"
  }
  Response:
  {
    "id": "integer",
    "resolved_at": "datetime",
    "resolution_notes": "string"
  }
  ```
- `GET /api/v1/alarms/statistics/` - Get alarm statistics
  ```json
  Response:
  {
    "total_alarms": "integer",
    "recent_alarms": "integer",
    "subject_stats": [
      {
        "subject__name": "string",
        "subject__id": "integer",
        "count": "integer",
        "last_alarm": "datetime",
        "notification_success_rate": "float"
      }
    ],
    "date_stats": [
      {
        "timestamp__date": "date",
        "count": "integer",
        "notifications_sent": "integer",
        "notifications_failed": "integer"
      }
    ],
    "hour_stats": [
      {
        "hour": "integer",
        "count": "integer"
      }
    ],
    "notifications": {
      "sent": "integer",
      "delivered": "integer",
      "failed": "integer",
      "pending": "integer"
    },
    "time_range": {
      "start_date": "datetime",
      "end_date": "datetime",
      "days": "integer"
    }
  }
  ```
- `POST /api/v1/alarms/{id}/retry-notification/` - Retry a failed notification
  ```json
  Response:
  {
    "success": "boolean",
    "message": "string"
  }
  ```

### Notification Attempts
- `GET /api/v1/notification-attempts/` - List notification attempts
  ```json
  Response:
  {
    "count": "integer",
    "results": [
      {
        "id": "integer",
        "alarm": "integer",
        "recipient": "integer",
        "channel": "string",
        "status": "string",
        "sent_at": "datetime",
        "error_message": "string",
        "retry_count": "integer",
        "created_at": "datetime"
      }
    ]
  }
  ```
- `POST /api/v1/notification-attempts/` - Create notification attempt
- `GET /api/v1/notification-attempts/{id}/` - Get notification attempt details
  ```json
  Response:
  {
    "id": "integer",
    "alarm": "integer",
    "recipient": "integer",
    "channel": "string",
    "status": "string",
    "sent_at": "datetime",
    "error_message": "string",
    "retry_count": "integer",
    "created_at": "datetime"
  }
  ```
- `POST /api/v1/notification-attempts/{id}/mark-sent/` - Mark notification as sent
  ```json
  Response:
  {
    "id": "integer",
    "status": "SENT",
    "sent_at": "datetime"
  }
  ```
- `POST /api/v1/notification-attempts/{id}/mark-failed/` - Mark notification as failed
  ```json
  Request:
  {
    "error_message": "string"
  }
  Response:
  {
    "id": "integer",
    "status": "FAILED",
    "error_message": "string",
    "retry_count": "integer"
  }
  ```

### Custodians
- `GET /api/v1/custodians/` - List custodians
  ```json
  Response:
  {
    "count": "integer",
    "results": [
      {
        "id": "integer",
        "user": "integer",
        "phone_number": "string",
        "is_verified": "boolean",
        "created_at": "datetime"
      }
    ]
  }
  ```
- `GET /api/v1/custodians/{id}/` - Get custodian
- `POST /api/v1/custodians/` - Create custodian (Not implemented yet)
- `PUT /api/v1/custodians/{id}/` - Update custodian (Not implemented yet)
- `DELETE /api/v1/custodians/{id}/` - Delete custodian (Not implemented yet)

### Export Endpoints (Web UI only, not API)
- `GET /alarms/export/csv/` - Export alarms as CSV
- `GET /alarms/export/excel/` - Export alarms as Excel

### Webhooks
- `POST /webhooks/twilio/status/` - Twilio status callback
  ```json
  Request:
  {
    "MessageSid": "string",
    "MessageStatus": "string",
    "To": "string",
    "From": "string",
    "ErrorCode": "string",
    "ErrorMessage": "string"
  }
  Response:
  {
    "status": "success"
  }
  ```

## Request/Response Format

### Request Format
```json
{
    "method": "POST",
    "endpoint": "/api/v1/subjects/",
    "headers": {
        "Authorization": "Bearer <token>",
        "Content-Type": "application/json"
    },
    "body": {
        "name": "John Doe",
        "date_of_birth": "1990-01-01",
        "gender": "M"
    }
}
```

### Response Format
```json
{
    "status": "success",
    "data": {
        "id": 1,
        "name": "John Doe",
        "date_of_birth": "1990-01-01",
        "gender": "M",
        "created_at": "2024-03-20T10:00:00Z"
    },
    "meta": {
        "page": 1,
        "per_page": 10,
        "total": 100
    }
}
```

### Error Format
```json
{
    "status": "error",
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "errors": [
        {
            "field": "name",
            "message": "Name is required"
        }
    ]
}
```

## Error Handling

### API Errors
1. **Validation Errors**
   - Invalid input
   - Missing fields
   - Format errors
   - Type errors

2. **Authentication Errors**
   - Invalid token
   - Expired token
   - Missing token
   - Invalid credentials

3. **Authorization Errors**
   - Permission denied
   - Role required
   - Scope required
   - Resource unavailable

### Recovery Procedures
1. **Automatic Recovery**
   - Token refresh
   - Rate limit reset
   - Error logging
   - Status updates

2. **Manual Intervention**
   - Token revocation
   - Rate limit adjustment
   - Error resolution
   - Access restoration

## Best Practices

### API Design
1. **Standards**
   - RESTful principles
   - HTTP methods
   - Status codes
   - Error handling

2. **Documentation**
   - OpenAPI/Swagger
   - Examples
   - Authentication
   - Rate limits

### Performance
1. **Optimization**
   - Response caching
   - Query optimization
   - Pagination
   - Filtering

2. **Scalability**
   - Load balancing
   - Rate limiting
   - Resource limits
   - Service discovery

## Testing

### API Tests
1. **Unit Tests**
   - Endpoint tests
   - Validation tests
   - Authentication tests
   - Authorization tests

2. **Integration Tests**
   - Flow tests
   - Error tests
   - Rate limit tests
   - Cache tests

### Performance Tests
1. **Load Testing**
   - Concurrent requests
   - Response times
   - Error rates
   - Resource usage

2. **Stress Testing**
   - High load
   - Error conditions
   - Recovery testing
   - Stability testing

## Rate Limiting
- Default limit: 100 requests per minute per user
- Rate limit headers:
  - `X-RateLimit-Limit`: Maximum requests per window
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Time when the rate limit resets

## API Versioning
- Current version: v1
- Version is specified in URL: `/api/v1/`
- Backward compatibility is maintained within major versions
- Breaking changes will result in a new major version

## Best Practices
1. Always include authentication token in requests
2. Use appropriate HTTP methods
3. Handle rate limiting gracefully
4. Implement proper error handling
5. Use pagination for list endpoints
6. Follow RESTful conventions
7. Validate input data
8. Use proper content types
9. Implement proper logging
10. Monitor API usage

## Updated API Documentation (April 2024)

### Alarms API
The Alarms API provides endpoints for managing alarms and their notification attempts. All endpoints require authentication and use HTTPS.

#### Endpoints

##### Alarms
- `GET /api/v1/alarms/` - List alarms
  ```json
  Response:
  {
    "count": "integer",
    "results": [
      {
        "id": "integer",
        "subject": "integer",
        "qr_code": "integer",
        "timestamp": "datetime",
        "location": "string",
        "is_test": "boolean",
        "notification_status": "string",
        "notification_sent": "boolean",
        "notification_error": "string",
        "notification_attempt_count": "integer",
        "last_attempt": "datetime",
        "whatsapp_message_id": "string",
        "resolved_at": "datetime",
        "resolution_notes": "string",
        "created_at": "datetime",
        "updated_at": "datetime"
      }
    ]
  }
  ```

- `POST /api/v1/alarms/` - Create alarm
  ```json
  Request:
  {
    "subject": "integer",
    "qr_code": "integer",
    "location": "string",
    "is_test": "boolean"
  }
  Response:
  {
    "id": "integer",
    "subject": "integer",
    "qr_code": "integer",
    "location": "string",
    "is_test": "boolean",
    "notification_status": "PENDING",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
  ```

- `GET /api/v1/alarms/{id}/` - Get alarm details
  ```json
  Response:
  {
    "id": "integer",
    "subject": "integer",
    "qr_code": "integer",
    "timestamp": "datetime",
    "location": "string",
    "is_test": "boolean",
    "notification_status": "string",
    "notification_sent": "boolean",
    "notification_error": "string",
    "notification_attempt_count": "integer",
    "last_attempt": "datetime",
    "whatsapp_message_id": "string",
    "resolved_at": "datetime",
    "resolution_notes": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
  ```

- `PUT /api/v1/alarms/{id}/` - Update alarm
- `DELETE /api/v1/alarms/{id}/` - Delete alarm
- `POST /api/v1/alarms/{id}/resolve/` - Resolve alarm
  ```json
  Request:
  {
    "resolution_notes": "string"
  }
  Response:
  {
    "id": "integer",
    "resolved_at": "datetime",
    "resolution_notes": "string"
  }
  ```
- `GET /api/v1/alarms/statistics/` - Get alarm statistics
  ```json
  Response:
  {
    "total_alarms": "integer",
    "recent_alarms": "integer",
    "subject_stats": [
      {
        "subject__name": "string",
        "subject__id": "integer",
        "count": "integer",
        "last_alarm": "datetime",
        "notification_success_rate": "float"
      }
    ],
    "date_stats": [
      {
        "timestamp__date": "date",
        "count": "integer",
        "notifications_sent": "integer",
        "notifications_failed": "integer"
      }
    ],
    "hour_stats": [
      {
        "hour": "integer",
        "count": "integer"
      }
    ],
    "notifications": {
      "sent": "integer",
      "delivered": "integer",
      "failed": "integer",
      "pending": "integer"
    },
    "time_range": {
      "start_date": "datetime",
      "end_date": "datetime",
      "days": "integer"
    }
  }
  ```
- `POST /api/v1/alarms/{id}/retry-notification/` - Retry a failed notification
  ```json
  Response:
  {
    "success": "boolean",
    "message": "string"
  }
  ```

##### Notification Attempts
- `GET /api/v1/notification-attempts/` - List notification attempts
  ```json
  Response:
  {
    "count": "integer",
    "results": [
      {
        "id": "integer",
        "alarm": "integer",
        "recipient": "integer",
        "channel": "string",
        "status": "string",
        "sent_at": "datetime",
        "error_message": "string",
        "retry_count": "integer",
        "created_at": "datetime"
      }
    ]
  }
  ```

- `POST /api/v1/notification-attempts/` - Create notification attempt
- `GET /api/v1/notification-attempts/{id}/` - Get notification attempt details
  ```json
  Response:
  {
    "id": "integer",
    "alarm": "integer",
    "recipient": "integer",
    "channel": "string",
    "status": "string",
    "sent_at": "datetime",
    "error_message": "string",
    "retry_count": "integer",
    "created_at": "datetime"
  }
  ```

- `POST /api/v1/notification-attempts/{id}/mark-sent/` - Mark notification as sent
  ```json
  Response:
  {
    "id": "integer",
    "status": "SENT",
    "sent_at": "datetime"
  }
  ```

- `POST /api/v1/notification-attempts/{id}/mark-failed/` - Mark notification as failed
  ```json
  Request:
  {
    "error_message": "string"
  }
  Response:
  {
    "id": "integer",
    "status": "FAILED",
    "error_message": "string",
    "retry_count": "integer"
  }
  ```

#### Test Results
All API endpoints have been thoroughly tested with the following test cases:

##### Alarm API Tests
- ✅ Creating a new alarm
- ✅ Listing all alarms
- ✅ Retrieving a single alarm
- ✅ Updating an alarm
- ✅ Deleting an alarm
- ✅ Resolving an alarm
- ✅ Viewing alarm statistics
- ✅ Retrying a failed notification

##### Notification Attempt API Tests
- ✅ Listing notification attempts
- ✅ Creating a notification attempt
- ✅ Retrieving a single notification attempt
- ✅ Marking a notification as sent
- ✅ Marking a notification as failed

All tests are passing with proper HTTPS support and secure cookie handling. The API endpoints handle both success and error cases appropriately, with proper validation of input data and consistent response formats.

#### Notes
- All API endpoints require authentication
- The API uses HTTPS for secure communication
- Responses use standard HTTP status codes (200, 201, 400, 401, 403, 404, etc.)
- Notification status values are uppercase: PENDING, PROCESSING, ACCEPTED, SENT, DELIVERED, FAILED, ERROR
- Notification channels supported: whatsapp, email, sms
- The API is versioned under `/api/v1/`
- All timestamps are in ISO 8601 format
- All endpoints support pagination
- Rate limiting is enabled (100/day for anonymous users, 1000/day for authenticated users) 