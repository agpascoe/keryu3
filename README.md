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
