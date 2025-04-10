# User Management System

## Overview
The User Management System is a core component of Keryu that handles user registration, authentication, and profile management. It provides a secure and user-friendly interface for managing user accounts and their associated roles and permissions.

## Models

### User Model
```python
class User(AbstractUser):
    PHONE_VERIFIED = 'phone_verified'
    EMAIL_VERIFIED = 'email_verified'
    BOTH_VERIFIED = 'both_verified'
    NOT_VERIFIED = 'not_verified'

    VERIFICATION_STATUS_CHOICES = [
        (PHONE_VERIFIED, 'Phone Verified'),
        (EMAIL_VERIFIED, 'Email Verified'),
        (BOTH_VERIFIED, 'Both Verified'),
        (NOT_VERIFIED, 'Not Verified'),
    ]

    phone_number = PhoneNumberField(unique=True)
    email = models.EmailField(unique=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default=NOT_VERIFIED
    )
    phone_verified_at = models.DateTimeField(null=True, blank=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_login_device = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### UserProfile Model
```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = PhoneNumberField(blank=True, null=True)
    preferred_language = models.CharField(max_length=10, default='en')
    notification_preferences = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## Features

### User Management
1. **Registration**
   - Phone number verification
   - Email verification
   - Profile creation
   - Welcome notification

2. **Authentication**
   - Multi-factor authentication
   - Session management
   - Device tracking
   - IP tracking

3. **Profile Management**
   - Profile picture
   - Contact information
   - Emergency contacts
   - Preferences

### Verification System
1. **Phone Verification**
   - SMS code generation
   - Code validation
   - Rate limiting
   - Expiration handling

2. **Email Verification**
   - Verification link
   - Link expiration
   - Resend capability
   - Status tracking

3. **Status Management**
   - Combined status
   - Verification timestamps
   - Status updates
   - History logging

## Tasks and Background Jobs

### Verification Processing
1. **Code Generation**
   - Secure generation
   - Storage management
   - Expiration handling
   - Cleanup tasks

2. **Notification Sending**
   - Channel selection
   - Template usage
   - Delivery tracking
   - Error handling

### Cleanup Tasks
1. **Session Management**
   - Expired session cleanup
   - Device tracking
   - IP tracking
   - Activity logging

2. **Profile Management**
   - Unused profile cleanup
   - Image optimization
   - Storage management
   - Cache updates

## API Endpoints

### User Management
- `GET /api/users/` - List users
- `POST /api/users/` - Create user
- `GET /api/users/{id}/` - Get user details
- `PUT /api/users/{id}/` - Update user
- `DELETE /api/users/{id}/` - Delete user

### Profile Management
- `GET /api/users/{id}/profile/` - Get profile
- `PUT /api/users/{id}/profile/` - Update profile
- `POST /api/users/{id}/profile/picture/` - Upload picture
- `DELETE /api/users/{id}/profile/picture/` - Delete picture

### Verification
- `POST /api/users/{id}/verify/phone/` - Send phone code
- `POST /api/users/{id}/verify/phone/confirm/` - Confirm phone
- `POST /api/users/{id}/verify/email/` - Send email link
- `GET /api/users/verify/email/{token}/` - Confirm email

## Views and Templates

### User Views
1. **Registration**
   - Phone input
   - Email input
   - Verification forms
   - Success messages

2. **Profile**
   - Information display
   - Edit form
   - Picture upload
   - Preferences

3. **Dashboard**
   - Account status
   - Recent activity
   - Quick actions
   - Notifications

### Verification Views
1. **Phone Verification**
   - Code input
   - Resend option
   - Status display
   - Error handling

2. **Email Verification**
   - Link display
   - Status check
   - Resend option
   - Success page

## Error Handling

### Processing Errors
1. **Verification Errors**
   - Invalid codes
   - Expired links
   - Rate limits
   - Network issues

2. **Profile Errors**
   - Upload failures
   - Validation errors
   - Storage issues
   - Permission errors

### Recovery Procedures
1. **Automatic Recovery**
   - Code regeneration
   - Link resending
   - Error logging
   - Status updates

2. **Manual Intervention**
   - Support contact
   - Manual verification
   - Profile recovery
   - Account restoration

## Best Practices

### Security
1. **Authentication**
   - Password policies
   - Session security
   - Rate limiting
   - IP blocking

2. **Data Protection**
   - Encryption
   - Secure storage
   - Access logs
   - Compliance

### Performance
1. **Optimization**
   - Cache usage
   - Image optimization
   - Query optimization
   - Resource management

2. **Monitoring**
   - User activity
   - Error rates
   - Performance metrics
   - Resource usage

## Testing

### Unit Tests
- Model tests
- View tests
- Form tests
- Service tests

### Integration Tests
- API tests
- Authentication tests
- File handling
- Database operations

### Manual Testing
- Registration flow
- Verification process
- Profile management
- Error scenarios 