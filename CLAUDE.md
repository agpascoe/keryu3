# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Keryu is a Django-based subject tracking system that manages vulnerable persons (children, elders, or persons with disabilities) using QR codes and multi-channel messaging notifications. The system allows custodians to register subjects, generate QR codes for tracking, and receive notifications when QR codes are scanned.

## Key Django Applications

### Core Applications
- **core/**: Django project configuration, settings, Celery setup, and messaging infrastructure
- **custodians/**: User management for custodians (caretakers) with phone verification
- **subjects/**: Subject management and QR code generation/management
- **alarms/**: Alarm system triggered by QR code scans with notification handling
- **notifications/**: Multi-channel messaging providers (WhatsApp, SMS, Email)

### Key Models Architecture
- **Custodian**: Extends User model with phone verification and contact info
- **Subject**: Tracked persons with medical info, linked to custodians
- **QRCode**: Generated codes for subjects with active/inactive states
- **Alarm**: Events triggered when QR codes are scanned
- **NotificationAttempt**: Tracks notification delivery across channels

## Development Environment Commands

### Setup and Activation
```bash
# Activate conda environment and navigate to project
source /home/ubuntu/miniconda3/etc/profile.d/conda.sh
conda activate keryu
cd /home/ubuntu/keryu3
```

### Enhanced Development Environment Script
Use the `./dev_env.sh` script for streamlined development:

```bash
# Check status
./dev_env.sh status

# Start server (auto-navigation and environment validation)
./dev_env.sh start

# Stop server
./dev_env.sh stop

# Restart server
./dev_env.sh restart

# Run tests
./dev_env.sh test

# Create test data
./dev_env.sh data

# View logs
./dev_env.sh logs

# Get help
./dev_env.sh help
```

### Development Server
```bash
# Start development server with dev settings (enhanced script recommended)
./dev_startup.sh

# Or manually:
DJANGO_SETTINGS_MODULE=core.settings_dev python manage.py runserver 0.0.0.0:8000
```

### Production Deployment
```bash
# Start all production services (Nginx, Redis, Celery, Gunicorn)
./startup.sh

# Stop all services
./shutdown.sh
```

### Database Management
```bash
# Run migrations
python manage.py migrate

# Create test data
python manage.py create_test_data

# Clear all data (development only)
python manage.py clear_data
```

### Testing
```bash
# Run all tests with pytest
pytest

# Run specific test categories
python dev_test.py test           # All tests
python dev_test.py notification   # Notification tests
python dev_test.py qr             # QR code tests
python dev_test.py alarm          # Alarm tests

# Run Django tests
python manage.py test

# Test specific app
python manage.py test alarms
python manage.py test subjects
```

### Code Quality
```bash
# Format code with Black
black .

# Lint code
flake8

# Check Django configuration
python manage.py check
```

### Celery Background Tasks
```bash
# Start Celery worker (development)
celery -A core worker --loglevel=info

# Start Celery beat scheduler
celery -A core beat --loglevel=info
```

## Architecture Notes

### Settings Configuration
- **core/settings.py**: Production settings
- **core/settings_dev.py**: Development settings with DEBUG=True, console notifications
- **core/test_settings.py**: Test-specific settings

### Multi-Channel Messaging System
The notification system uses a provider pattern with fallback channels:
1. **Primary**: Meta WhatsApp Business API
2. **Fallback**: Twilio WhatsApp 
3. **Final Fallback**: Twilio SMS

**Development Mode Features:**
- All notifications logged to console instead of being sent
- Console messages include detailed formatting and debug information
- Development dashboard provides notification testing tools
- Real-time system monitoring (CPU, memory, disk usage)

### QR Code System
- Each subject can have multiple QR codes, but only one active at a time
- QR codes link to URLs that trigger alarm creation when accessed
- QR code images are generated using the `qrcode` library and stored in media/qr_codes/

### Background Task Processing
- **Celery** handles asynchronous tasks (notifications, QR generation)
- **Redis** serves as message broker and result backend
- Separate queues for different task types (alarms, subjects)
- Periodic tasks for cleanup and processing pending alarms

### Phone Number Handling
- Uses `django-phonenumber-field` for international phone number validation
- Currently optimized for Mexican phone numbers (+52 country code)
- Accepts multiple formats (10 digits, 12 digits with 52, 13 digits with 521)
- WhatsApp verification required for custodian registration with 4-digit codes
- 15-minute verification code expiration
- Verification attempt tracking and rate limiting

## Key File Locations

### Configuration Files
- `environment.yml`: Conda environment specification
- `requirements.txt`: Python dependencies
- `pytest.ini`: Test configuration
- `.cursor/rules/generalrules.mdc`: Cursor AI development guidelines

### Database
- `db.sqlite3`: SQLite database (development)
- PostgreSQL used in production

### Static Files and Media
- `static/`: Static assets (CSS, JS, images)
- `staticfiles/`: Collected static files for production
- `media/qr_codes/`: Generated QR code images
- `media/subject_photos/`: Subject photo uploads

### Scripts and Tools
- `dev_env.sh`: **Enhanced development environment script** (recommended)
- `dev_test.py`: Development testing utility
- `startup.sh` / `shutdown.sh`: Production service management
- `dev_startup.sh`: Development server startup (legacy)
- `dev_dashboard.py`: Development dashboard with monitoring and controls

## Security Considerations

- Environment variables for sensitive configuration (API keys, database credentials)
- SSL/TLS certificates managed via Let's Encrypt
- Phone verification required for account activation
- Role-based access control (custodians can only manage their own subjects)
- Staff users excluded from statistical dashboards

## Development Guidelines

### Following Cursor Rules
When implementing features, follow the three-step process defined in .cursor/rules/:
1. Analyze the problem and propose 3+ solution options
2. Create detailed implementation plan (Plan_xxx.md files) 
3. Follow software engineering principles for clean, efficient code

**Important Note**: Always reference `scope.md`, `technical_spec.md`, and `README.md` before proposing solutions to ensure alignment with system architecture and requirements.

### Testing Strategy
- Console-based notifications in development for easy testing
- Test users and data creation via management commands
- Comprehensive test coverage for critical paths (QR scanning, notifications)
- API testing with JWT authentication

### Key URLs for Development
- Main app: http://localhost:8000/
- **Development Dashboard**: http://localhost:8000/dev/ (real-time monitoring and controls)
- Admin interface: http://localhost:8000/admin/
- **API documentation**: http://localhost:8000/swagger/
- QR scan test: http://localhost:8000/qr/{uuid}/

## Common Development Tasks

### Daily Development Workflow
```bash
# 1. Daily Start
cd /home/ubuntu/keryu3
conda activate keryu
./dev_env.sh start

# 2. Making Changes - Edit code, then:
./dev_env.sh test
python manage.py check

# 3. Database Changes
python manage.py makemigrations
python manage.py migrate

# 4. End of Day
./dev_env.sh stop
```

### Common Troubleshooting Issues

#### "manage.py not found" Error
**Root Cause**: Running commands from wrong directory
**Solution**: Use `./dev_env.sh start` (auto-navigates) or manually `cd /home/ubuntu/keryu3`

#### Port 8000 Already in Use
**Solution**: `./dev_env.sh restart` (automatically handles port conflicts)

#### Conda Environment Issues  
**Solution**: `./dev_env.sh start` will automatically activate the environment

### Adding New Notification Channels
1. Create provider class in `notifications/providers.py`
2. Update channel routing in messaging system
3. Add configuration settings
4. Test with development console provider first

### QR Code Customization  
- QR code parameters configured in `subjects/utils.py`
- Images generated on-demand with proper error handling
- Cache-busting and retry mechanisms implemented
- Toggle active/inactive status with real-time AJAX updates

### Database Schema Changes
1. Create migration: `python manage.py makemigrations`
2. Review migration file
3. Apply: `python manage.py migrate`
4. Update test fixtures if needed

### Background Task Development
1. Define task in appropriate app's `tasks.py`
2. Add to Celery routing in `core/celery.py`
3. Test with development settings (synchronous execution)
4. Monitor with Celery logs in production