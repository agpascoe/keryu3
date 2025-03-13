# Keryu QR Code Management System

A Django-based system for managing QR codes that help track and monitor subjects (children, elderly) and send instant notifications to custodians when assistance is needed.

## Features

### QR Code Management
- Generate unique QR codes for each subject
- Activate/deactivate QR codes as needed
- Download QR codes for printing
- View QR code scanning history
- Only one active QR code per subject at a time

### Alarm System
- Instant alarm creation when QR codes are scanned
- Location tracking support
- Real-time WhatsApp notifications to custodians
- Alarm history and statistics

### Security
- Role-based access control
- Secure QR code generation with UUIDs
- No personal information stored in QR codes
- Login required for management functions

## Installation

1. Clone the repository:
```bash
git clone https://github.com/agpascoe/keryu3.git
cd keryu3
```

2. Create and activate a conda environment:
```bash
conda create -n keryu3 python=3.10
conda activate keryu3
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```

Edit `.env` and add your configuration:
```
DJANGO_SECRET_KEY=your_secret_key
WHATSAPP_ACCESS_TOKEN=your_whatsapp_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Start the development server:
```bash
python manage.py runserver
```

## Usage

### Managing QR Codes

1. Log in to your account
2. Navigate to "QR Codes" in the navigation menu
3. Select a subject from the dropdown to filter QR codes
4. Click "Generate New QR Code" to create a QR code
5. Use the action buttons to:
   - View the QR code
   - Download the QR code
   - Activate/deactivate the QR code
   - Delete the QR code

### Scanning QR Codes

1. Access the QR code's URL or scan with a QR code reader
2. If location services are enabled, the system will record the location
3. An alarm is created and the custodian receives a WhatsApp notification
4. The scan result page shows the status and details

### WhatsApp Notifications

Custodians receive notifications containing:
- Subject's name
- Timestamp of the scan
- Location link (if available)
- Quick response options

## API Documentation

### QR Code Endpoints

- `GET /subjects/qr-codes/` - List QR codes
- `POST /subjects/qr/generate/` - Generate new QR code
- `GET /subjects/qr/<uuid>/image/` - View QR code image
- `GET /subjects/qr/<uuid>/download/` - Download QR code
- `POST /subjects/qr/<uuid>/activate/` - Activate QR code
- `POST /subjects/qr/<uuid>/deactivate/` - Deactivate QR code
- `POST /subjects/qr/<uuid>/delete/` - Delete QR code
- `GET /subjects/qr/<uuid>/scan/` - Scan QR code

## Development

### Running Tests

```bash
python manage.py test subjects.tests -v 2
```

### Code Style

Follow PEP 8 guidelines and Django's coding style:
- Use 4 spaces for indentation
- Keep lines under 79 characters
- Write docstrings for all functions and classes

## Troubleshooting

### Common Issues

1. WhatsApp notifications not sending:
   - Check WhatsApp API credentials
   - Verify internet connectivity
   - Check Celery worker status

2. QR codes not scanning:
   - Ensure the QR code is active
   - Check internet connectivity
   - Verify the URL is accessible

### Getting Help

For support:
1. Check the issues on GitHub
2. Contact the development team
3. Review the error logs

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 