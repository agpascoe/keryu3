# Keryu - QR Code Monitoring System

A Django-based system for monitoring QR code scans and sending WhatsApp notifications.

## Features

- QR Code scanning and validation
- Real-time WhatsApp notifications
- Asynchronous task processing with Celery
- Template-based messaging system
- Comprehensive error handling and logging

## Prerequisites

- Python 3.8+
- PostgreSQL
- Redis (for Celery)
- WhatsApp Business API access
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

6. Start Redis server:
```bash
redis-server
```

7. Start Celery worker:
```bash
celery -A keryu worker -l info
```

8. Run the development server:
```bash
python manage.py runserver
```

## WhatsApp Template Setup

1. Log in to your Meta Developer Account
2. Navigate to WhatsApp > Getting Started
3. Create a new template with the following details:
   - Name: qr_is_on
   - Language: en_US
   - Category: UTILITY
   - Body: "Hello, the qr of {{Subject}} has been read at {{Timestamp}}"
4. Wait for template approval (usually takes 24-48 hours)

## Testing

1. Run the test script to verify WhatsApp integration:
```bash
python test_whatsapp.py
```

2. Run Django tests:
```bash
python manage.py test
```

## Project Structure

```
keryu/
├── alarms/              # Alarm monitoring system
├── notifications/       # Notification providers
├── subjects/           # Subject management
├── core/               # Core functionality
├── templates/          # HTML templates
├── static/            # Static files
├── manage.py
├── requirements.txt
└── .env
```

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