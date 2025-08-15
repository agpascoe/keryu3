# Keryu Development Environment

## Overview
This document describes how to work with the Keryu development environment for testing and improving the system.

## Quick Start

### 1. Activate Environment
```bash
source /home/ubuntu/miniconda3/etc/profile.d/conda.sh
conda activate keryu
cd /home/ubuntu/keryu3
```

### 2. Start Development Server
```bash
DJANGO_SETTINGS_MODULE=core.settings_dev python manage.py runserver 0.0.0.0:8000
```

### 3. Access the Application
- **Main Application**: http://localhost:8000/
- **Admin Interface**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8000/api/

## Development Features

### Console Notifications
In development mode, all notifications are logged to the console instead of being sent via WhatsApp/SMS. You'll see messages like:

```
============================================================
📱 CONSOLE NOTIFICATION - 2025-07-09 00:15:58
📞 To: +1234567890
💬 Message: Alert: Test Subject has been located at 2025-07-09 00:15:58
📋 Raw data: {'subject_name': 'Test Subject', 'timestamp': '2025-07-09 00:15:58', 'location': 'Test Location'}
============================================================
```

### Test Data
Use the development test script to create test data:

```bash
# Run all tests
python dev_test.py test

# Create test data
python dev_test.py create-data

# Test specific features
python dev_test.py notification
python dev_test.py qr
python dev_test.py alarm
python dev_test.py db
```

### Test Users
The system creates these test users:
- **admin** (admin@keryu.com) - Admin user
- **custodian1** (custodian1@keryu.com) - John Doe
- **custodian2** (custodian2@keryu.com) - Jane Smith

## Development Settings

### Key Differences from Production
- `DEBUG = True`
- SSL/security settings disabled
- Console email backend
- Celery tasks run synchronously
- Local memory cache
- Console notification provider
- No rate limiting

### Logging
Development logs are written to `dev.log` with DEBUG level logging enabled.

## Testing QR Codes

### Generate QR Code
1. Create a subject in the admin interface
2. Generate a QR code for the subject
3. Access the QR code URL: `http://localhost:8000/qr/{uuid}/`

### Test QR Code Scanning
1. Click on the QR code URL to simulate scanning
2. Choose situation type (TEST, INJURED, LOST, CONTACT)
3. Fill in details and submit
4. Check console for notification logs

## API Testing

### Authentication
The API uses JWT authentication. Get a token:

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Test Endpoints
```bash
# List subjects (requires authentication)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/subjects/

# Create alarm
curl -X POST http://localhost:8000/qr/{uuid}/ \
  -H "Content-Type: application/json" \
  -d '{"situation_type": "TEST", "description": "Test alarm"}'
```

## Database

### Current Data
- **Users**: 7 (including test users)
- **Custodians**: 7
- **Subjects**: 5 (including test subjects)
- **QR Codes**: 3
- **Alarms**: 2 (from testing)

### Reset Database
To start fresh:

```bash
# Remove database
rm db.sqlite3

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Create test data
python dev_test.py create-data
```

## Troubleshooting

### Server Won't Start
1. Check if conda environment is activated
2. Verify Django settings: `python manage.py check`
3. Check for port conflicts: `lsof -i :8000`

### Import Errors
1. Ensure conda environment is activated
2. Check if all dependencies are installed: `pip list`
3. Verify Python path: `python -c "import django; print(django.__file__)"`

### Database Issues
1. Check migrations: `python manage.py showmigrations`
2. Run migrations: `python manage.py migrate`
3. Check database connection: `python dev_test.py db`

## Development Workflow

### 1. Make Changes
- Edit code in the appropriate Django app
- Test changes with development server

### 2. Test Features
- Use `python dev_test.py test` for comprehensive testing
- Test specific features with individual test commands
- Check console for notification logs

### 3. Create Test Data
- Use `python dev_test.py create-data` for fresh test data
- Or create data through the admin interface

### 4. Test Web Interface
- Access http://localhost:8000/ for main application
- Use admin interface for data management
- Test QR code scanning functionality

## Next Steps

### Add Debugging Tools
Once basic functionality is working, you can add:
- Django Debug Toolbar
- Additional logging
- Performance monitoring

### Production Testing
- Test with real WhatsApp API credentials
- Test with PostgreSQL database
- Test with Redis for Celery

### Feature Development
- Add new notification channels
- Improve QR code generation
- Enhance alarm management
- Add reporting features 