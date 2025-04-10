# Phone and Email Verification System

## Overview
This document details the implementation of the dual verification system in Keryu: phone verification using a 4-digit code and email verification using a secure link. Each system is designed with different security considerations and user experience requirements.

## 1. Database Models

### Phone Verification
```python
class PhoneVerificationAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(null=True)
    is_verified = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)
    message_id = models.CharField(max_length=255, null=True)  # Twilio message ID
    channel = models.CharField(max_length=20)  # SMS/WhatsApp

    class Meta:
        indexes = [
            models.Index(fields=['user', 'verification_code']),
            models.Index(fields=['created_at']),
        ]
```

### Email Verification
```python
class EmailVerificationAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(null=True)
    is_verified = models.BooleanField(default=False)
    email_id = models.CharField(max_length=255, null=True)  # Twilio email ID

    class Meta:
        indexes = [
            models.Index(fields=['user', 'token']),
            models.Index(fields=['created_at']),
        ]
```

### User Verification Status
```python
class VerificationStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    phone_verified_at = models.DateTimeField(null=True)
    email_verified_at = models.DateTimeField(null=True)
    
    @property
    def is_fully_verified(self):
        return self.phone_verified and self.email_verified
```

## 2. Security Measures

### Phone Verification Security
1. **Code Generation**:
   - 4-digit numeric code
   - Randomly generated using cryptographic functions
   - No sequential or pattern-based codes

2. **Attempt Limiting**:
   - Maximum 3 attempts per code
   - 15-minute expiration
   - Rate limiting on code generation (3 per hour)

3. **Storage Security**:
   - Codes stored using Django's password hashing
   - Separate attempt tracking
   - Automatic cleanup of expired codes

4. **Delivery Security**:
   - Channel selection based on system parameters
   - Delivery confirmation tracking
   - Fallback channel support

### Email Verification Security
1. **Token Generation**:
   - Secure token using Django's signing module
   - Includes user ID and timestamp
   - Salt-based signing

2. **Link Security**:
   - One-time use links
   - 24-hour expiration
   - HTTPS enforced
   - Domain validation

3. **Storage Security**:
   - Tokens stored in hashed format
   - Automatic cleanup of expired tokens
   - Attempt tracking for analytics

4. **Delivery Security**:
   - Twilio email service
   - SPF and DKIM enabled
   - Delivery tracking
   - HTML/Text alternative versions

## 3. Frontend Implementation

### Phone Verification UI
```html
<!-- Phone Verification Form -->
<div class="verification-form">
    <h3>Enter Verification Code</h3>
    <p>We've sent a 4-digit code to your phone</p>
    
    <form method="POST" action="{% url 'verify_phone' %}">
        {% csrf_token %}
        <div class="code-input-group">
            <input type="text" maxlength="1" pattern="[0-9]" required>
            <input type="text" maxlength="1" pattern="[0-9]" required>
            <input type="text" maxlength="1" pattern="[0-9]" required>
            <input type="text" maxlength="1" pattern="[0-9]" required>
        </div>
        
        <div class="timer">Code expires in: <span id="countdown">15:00</span></div>
        
        <button type="submit" class="btn btn-primary">Verify</button>
        <button type="button" class="btn btn-link" id="resendCode">
            Resend Code
        </button>
    </form>
</div>

<script>
// Auto-focus and navigation for code inputs
document.querySelectorAll('.code-input-group input').forEach((input, index) => {
    input.addEventListener('input', (e) => {
        if (e.target.value && index < 3) {
            e.target.nextElementSibling.focus();
        }
    });
});

// Countdown timer
function startCountdown(duration) {
    let timer = duration;
    const countdown = document.getElementById('countdown');
    
    const interval = setInterval(() => {
        const minutes = parseInt(timer / 60, 10);
        const seconds = parseInt(timer % 60, 10);
        
        countdown.textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
        
        if (--timer < 0) {
            clearInterval(interval);
            countdown.textContent = 'Expired';
        }
    }, 1000);
}

startCountdown(15 * 60); // 15 minutes
</script>
```

### Email Verification Templates
```html
<!-- Email Template -->
<!DOCTYPE html>
<html>
<head>
    <title>Verify Your Email - Keryu</title>
</head>
<body>
    <div class="email-container">
        <h1>Welcome to Keryu!</h1>
        <p>Hello {{ user_name }},</p>
        <p>Please verify your email address by clicking the button below:</p>
        
        <a href="{{ verification_url }}" class="verify-button">
            Verify Email Address
        </a>
        
        <p>This link will expire in 24 hours.</p>
        
        <p>If you didn't create a Keryu account, please ignore this email.</p>
    </div>
</body>
</html>
```

## 4. Error Handling and Recovery

### Phone Verification Errors
1. **Invalid Code Handling**:
   ```python
   def handle_verification_error(error):
       if isinstance(error, MaxAttemptsError):
           # Reset code and notify user
           send_new_code(user)
           return "Maximum attempts reached. New code sent."
       elif isinstance(error, ExpiredCodeError):
           return "Code expired. Please request a new one."
       elif isinstance(error, InvalidCodeError):
           return f"Invalid code. {3 - attempts} attempts remaining."
   ```

2. **Delivery Failures**:
   ```python
   def handle_delivery_error(error):
       if isinstance(error, TwilioDeliveryError):
           # Try fallback channel
           try_fallback_channel(user)
           return "Message delivery failed. Trying alternative method."
       elif isinstance(error, PhoneNumberInvalidError):
           return "Invalid phone number. Please update your contact information."
   ```

### Email Verification Errors
1. **Link Expiration**:
   ```python
   def handle_link_expiration(token):
       if is_token_expired(token):
           # Generate new token and send new email
           send_new_verification_email(user)
           return "Link expired. New verification email sent."
   ```

2. **Invalid Token Handling**:
   ```python
   def handle_token_error(error):
       if isinstance(error, InvalidTokenError):
           log_security_event(user, 'invalid_token_attempt')
           return "Invalid verification link."
       elif isinstance(error, AlreadyVerifiedError):
           return "Email already verified."
   ```

### Recovery Processes
1. **Phone Verification Recovery**:
   - Automatic code regeneration after max attempts
   - Channel fallback on delivery failure
   - Support for phone number updates
   - Manual verification by support (if needed)

2. **Email Verification Recovery**:
   - Automatic new link generation
   - Support for email address updates
   - Manual verification process
   - Account recovery options

## Implementation Notes

1. **Phone Verification Best Practices**:
   - Keep codes short (4 digits) for usability
   - Provide clear error messages
   - Show remaining attempts
   - Include countdown timer
   - Offer resend option with rate limiting

2. **Email Verification Best Practices**:
   - Use secure, signed tokens
   - Include clear call-to-action in emails
   - Provide both HTML and text versions
   - Include security warnings about sharing links
   - Clear expiration information

3. **General Security Considerations**:
   - Rate limiting on all endpoints
   - Logging of all verification attempts
   - Secure token generation and storage
   - Clear user communication
   - Proper error handling and recovery

4. **Monitoring and Maintenance**:
   - Track verification success rates
   - Monitor delivery success rates
   - Regular cleanup of expired tokens/codes
   - Analysis of common failure points
   - Regular security audits 