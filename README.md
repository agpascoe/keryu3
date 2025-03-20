# Keryu - Subject Tracking System

A Django-based system for managing and tracking subjects (children, elders, or persons with disabilities) using QR codes and WhatsApp notifications.

## Features

- Subject management (personal and medical information)
- QR code generation and management
- QR code scanning and alarm creation
- Real-time WhatsApp notifications
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

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/keryu.git
cd keryu
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following variables:
```env
# Database Configuration
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# WhatsApp API Configuration
WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Django Configuration
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Start Redis server:
```bash
redis-server
```

8. Start Celery worker:
```bash
celery -A keryu worker -l info
```

9. Run the development server:
```bash
python manage.py runserver
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
4. Wait for template approval (usually takes 24-48 hours)

## Usage

1. Log in as a custodian
2. Create a subject with their details
3. Generate a QR code for the subject
4. Print or download the QR code
5. When the QR code is scanned:
   - An alarm is created
   - Location is recorded (if available)
   - WhatsApp notification is sent to the custodian

## Project Structure

```
keryu/
├── alarms/              # Alarm and notification handling
├── core/               # Core settings and configuration
├── custodians/         # User management
├── notifications/      # WhatsApp integration
├── subjects/           # Subject and QR code management
├── templates/          # HTML templates
├── static/            # Static files
├── media/             # User-uploaded files
├── manage.py
├── requirements.txt
└── .env
```

## Development

### Running Tests
```bash
python manage.py test
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

For support, please open an issue in the GitHub repository or contact the development team. 