# Keryu - Subject Tracking System
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
A Django-based system for managing and tracking subjects (children, elders, or persons with disabilities) using QR codes and multi-channel messaging notifications.

## Features

- **Subject Management**: Create, update, and manage subjects in the system
- **QR Code Management**: 
  - Generate and manage QR codes for subjects
  - Toggle QR code active/inactive status with real-time updates
  - Visual status indicators for easy management
  - Automatic state management ensuring only one active QR per subject
  - **Recent Fixes and Improvements:**
    - Fixed buffer handling by resetting buffer position before saving images
    - Improved error handling with try/except blocks and proper error responses
    - Enhanced media handling using FileResponse and cache control headers
    - Added frontend resilience with error handlers and placeholder images
    - Implemented automatic retry mechanism with cache-busting
    - Improved logging with additional debug information and size tracking
    - Consolidated QR code generation with consistent parameters
    - Fixed file system permissions for staticfiles directory
- **Alarm System**: Configure and manage alarms for subjects
- Subject management (personal and medical information)
- QR code scanning and alarm creation
- Multi-channel messaging support:
  - Meta WhatsApp API (Primary)
  - Twilio WhatsApp (Fallback)
  - Twilio SMS (Fallback)
- Dynamic channel selection
- Consistent message formatting
- Location tracking support
- Email verification for new custodians
- Admin dashboard with real-time statistics
- Custodian dashboard with personalized views
- Comprehensive error handling and logging

## Security Features

- SSL/TLS encryption with Let's Encrypt
- Email verification required for new accounts
- Secure token-based verification system
- Development mode with instant verification option
- Staff users excluded from custodian statistics
- Role-based access control

## Documentation Structure

The system documentation is organized into the following sections:

1. **Core Documentation**
   - [Technical Specification](docs/technical_spec.md)
   - [Project Scope](docs/scope.md)
   - [Deployment Guide](docs/deployment_plan.md)

2. **Feature Documentation**
   - [Messaging System](docs/messaging.md)
   - [User Management](docs/users.md)
   - [Subject Management](docs/subjects.md)
   - [Alarm System](docs/alarms.md)
   - [Authentication](docs/auth.md)
   - [API Documentation](docs/api.md)

3. **System Documentation**
   - [Database Schema](docs/database.md)
   - [Task System](docs/tasks.md)
   - [Security](docs/security.md)
   - [Monitoring](docs/monitoring.md)

## Prerequisites

- Python 3.12+
- PostgreSQL
- Redis (for Celery)
- Nginx
- Let's Encrypt SSL certificates
- Meta WhatsApp Business API access
- Meta Developer Account
- Twilio Account (optional, for fallback channels)
- Domain name (for SSL certificates)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/keryu.git
cd keryu
```

2. Create and activate conda environment:
```bash
conda env create -f environment.yml
conda activate keryu
```

3. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```env
# Database Configuration
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# WhatsApp API Configuration (Primary Channel)
WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id

# Twilio Configuration (Optional Fallback Channels)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_phone_number
TWILIO_WHATSAPP_NUMBER=your_whatsapp_number

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Django Configuration
SECRET_KEY=your_secret_key
DEBUG=False
ALLOWED_HOSTS=keryu.mx,www.keryu.mx
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

## Running the Application

The application uses multiple services that need to run together:
- Nginx (web server and reverse proxy)
- Redis server (for Celery broker and result backend)
- Celery worker (for background tasks)
- Celery beat (for scheduled tasks)
- Gunicorn (WSGI server)

### Production Deployment
We provide a startup script that manages all these services:

1. Make the startup script executable:
```bash
chmod +x startup.sh
```

2. Run the startup script:
```bash
./startup.sh
```

The script will:
- Check for required services (Nginx, Redis, etc.)
- Verify SSL certificates
- Clean up any existing processes
- Activate the conda environment
- Start Redis server
- Collect static files and set permissions
- Start Celery worker with proper queues
- Start Celery beat scheduler
- Start Gunicorn with multiple workers
- Start and configure Nginx
- Verify all services are running correctly

To stop all services, you can either:
- Press Ctrl+C in the terminal where startup.sh is running
- Run these commands:
  ```bash
  sudo systemctl stop nginx
  pkill -f "celery worker"
  pkill -f "celery beat"
  pkill -f "gunicorn"
  sudo service redis-server stop
  ```

## WhatsApp Template Setup

1. Log in to your Meta Developer Account
2. Navigate to WhatsApp > Message Templates
3. Create a new template with the following details:
   - Name: qr_template_on_m
   - Language: en_US
   - Category: UTILITY
   - Body: "Alert: {{1}} has been located at {{2}}"
   - Variables:
     - {{1}}: Subject name
     - {{2}}: Timestamp
4. Wait for template approval (usually 24-48 hours)

## Usage

1. Log in as a custodian
2. Create a subject with their details
3. Generate a QR code for the subject
4. Test or use the QR code:
   - View the QR code's direct URL for testing
   - Click the URL to simulate QR code scanning
   - Print or download for physical use
5. When the QR code is scanned (or URL is accessed):
   - An alarm is created
   - Location is recorded (if available)
   - Notification is sent via configured channel:
     - Meta WhatsApp API (default)
     - Twilio WhatsApp (fallback)
     - Twilio SMS (fallback)

## Project Structure

```
keryu/
├── alarms/              # Alarm and notification handling
├── core/               # Core settings and configuration
├── custodians/         # User management
├── notifications/      # Multi-channel messaging integration
├── subjects/           # Subject and QR code management
├── templates/          # HTML templates
├── static/            # Static files
├── media/             # User-uploaded files
├── docs/              # Documentation
├── manage.py
├── requirements.txt
└── .env
```

## Development

### Running Tests
```bash
# Run all tests
python manage.py test

# Run messaging tests specifically
python -m pytest tests/test_messaging.py -vv
```

### Creating Test Data
```bash
python manage.py create_test_data
```

### Code Style
- Follow PEP 8 guidelines
- Use Black for code formatting
- Run flake8 for linting

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please:
1. Check the documentation in the `docs/` directory
2. Open an issue in the GitHub repository
3. Contact the development team 

## Custodian Registration

### Registration Process
1. Visit https://www.keryu.mx/custodians/register/
2. Fill in the required information:
   - First and last name
   - Email address (must be unique)
   - Password (following security requirements)
   - Mexican phone number (WhatsApp enabled)
3. Submit the form
4. Check WhatsApp for verification code
5. Enter the 4-digit verification code
6. Account is activated upon successful verification

### Phone Number Format
- Mexican numbers only (currently)
- Accepted formats:
  * 10 digits (e.g., 1234567890)
  * With country code (e.g., +521234567890)
  * Without + symbol (e.g., 521234567890)

### Password Requirements
- Minimum 8 characters
- Cannot be similar to personal information
- Cannot be a commonly used password
- Cannot be entirely numeric
- Must include a mix of characters

### Verification Process
1. Form submission creates inactive account
2. WhatsApp verification code is sent
3. Code valid for 15 minutes
4. Limited verification attempts
5. Option to resend code if needed

### Troubleshooting Registration
1. **Email Already Registered**
   - Use different email or recover existing account
   
2. **Phone Number Issues**
   - Ensure Mexican number format
   - Verify WhatsApp is active
   - Check for previous registration
   
3. **Verification Code Problems**
   - Wait for WhatsApp message (can take a few minutes)
   - Check phone number accuracy
   - Use resend code option if needed
   - Contact support if persistent issues

4. **Session Expiration**
   - Complete verification within 15 minutes
   - Restart registration if session expires 
