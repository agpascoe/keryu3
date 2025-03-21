# Keryu - Subject Tracking System

A Django-based system for managing and tracking subjects (children, elders, or persons with disabilities) using QR codes and multi-channel messaging notifications.

## Features

- Subject management (personal and medical information)
- QR code generation and management
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

- Email verification required for new accounts
- Secure token-based verification system
- Development mode with instant verification option
- Staff users excluded from custodian statistics
- Role-based access control

## Prerequisites

- Python 3.11+
- PostgreSQL
- Redis (for Celery)
- Meta WhatsApp Business API access
- Meta Developer Account
- Twilio Account (optional, for fallback channels)

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
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
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
- Redis server (for Celery broker and result backend)
- Celery worker (for background tasks)
- Celery beat (for scheduled tasks)
- Django development server

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
- Clean up any existing processes
- Activate the conda environment
- Start Redis server
- Start Celery worker with proper queues
- Start Celery beat scheduler
- Start Django development server
- Verify all services are running with the correct number of instances

Note: Django runs with two processes by default (main process + autoreloader), which is normal and expected behavior.

To stop all services, you can either:
- Press Ctrl+C in the terminal where startup.sh is running
- Run these commands:
  ```bash
  pkill -f "celery worker"
  pkill -f "celery beat"
  pkill -f "runserver"
  brew services stop redis
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
4. Print or download the QR code
5. When the QR code is scanned:
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