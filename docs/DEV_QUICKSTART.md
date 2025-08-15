# Keryu3 Development Quick Start Guide

## 🚀 5-Minute Setup

### Prerequisites
- Python 3.8+
- Conda (recommended) or pip
- Git

### Step 1: Clone and Navigate
```bash
cd /home/ubuntu
git clone <repository-url> keryu3
cd keryu3
```

### Step 2: Environment Setup
```bash
# Create and activate conda environment
conda create -n keryu python=3.11
conda activate keryu

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Database Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### Step 4: Start Development Server
```bash
# Use the enhanced development script
./dev_env.sh start

# Or manually
DJANGO_SETTINGS_MODULE=core.settings_dev python manage.py runserver 0.0.0.0:8000
```

### Step 5: Access Your Application
- **Main App**: http://localhost:8000/
- **Development Dashboard**: http://localhost:8000/dev/
- **Admin Panel**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8000/swagger/

## 🛠️ Development Scripts

### Enhanced Development Environment Script
```bash
# Check status
./dev_env.sh status

# Start server
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

### Key Features
- **Auto-navigation**: Automatically finds the correct project directory
- **Environment validation**: Checks Django, database, and dependencies
- **Smart error handling**: Provides clear error messages and solutions
- **Process management**: Properly starts/stops development server
- **Log viewing**: Quick access to development logs

## 🎯 Common Development Tasks

### Running Tests
```bash
# Run all tests
./dev_env.sh test

# Run specific app tests
python manage.py test subjects

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

### Database Operations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (development only)
python manage.py flush

# Create test data
./dev_env.sh data
```

### API Testing
```bash
# Access API documentation
http://localhost:8000/swagger/

# Test endpoints
curl http://localhost:8000/api/v1/subjects/

# Get authentication token
curl -X POST http://localhost:8000/api/v1/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'
```

## 🖥️ Development Dashboard

### Features
- **Real-time system monitoring**: CPU, memory, disk usage
- **Server control**: Start/stop/restart development server
- **Testing tools**: Run tests, check Django configuration
- **Log viewing**: Browse and view log files
- **QR code testing**: Test QR code generation
- **Notification testing**: Test SMS notifications

### Access
- URL: http://localhost:8000/dev/
- Auto-refreshes every 30 seconds
- Interactive controls for common tasks

## 🔧 Troubleshooting

### Common Issues

#### 1. "manage.py not found" Error
```bash
# Solution: Use the enhanced script
./dev_env.sh start

# Or navigate manually
cd /home/ubuntu/keryu3
```

#### 2. Port 8000 Already in Use
```bash
# The script will automatically handle this
./dev_env.sh restart

# Or manually
pkill -f "python manage.py runserver"
```

#### 3. Conda Environment Not Activated
```bash
# The script will automatically activate it
./dev_env.sh start

# Or manually
conda activate keryu
```

#### 4. Database Connection Issues
```bash
# Check database
python manage.py check --database default

# Reset database (development only)
python manage.py flush
```

### Getting Help
```bash
# View script help
./dev_env.sh help

# Check system status
./dev_env.sh status

# View logs
./dev_env.sh logs
```

## 📁 Project Structure

```
keryu3/
├── core/                   # Main Django project
│   ├── settings_dev.py    # Development settings
│   ├── dev_dashboard.py   # Development dashboard
│   └── urls.py           # URL configuration
├── subjects/              # Subjects app
├── alarms/               # Alarms app
├── custodians/           # Custodians app
├── notifications/        # Notifications app
├── templates/            # HTML templates
├── static/              # Static files
├── media/               # User uploaded files
├── tests/               # Test files
├── docs/                # Documentation
├── dev_env.sh           # Enhanced development script
├── dev_test.py          # Development testing
├── requirements.txt     # Python dependencies
└── manage.py           # Django management
```

## 🔄 Development Workflow

### 1. Daily Start
```bash
cd /home/ubuntu/keryu3
conda activate keryu
./dev_env.sh start
```

### 2. Making Changes
```bash
# Edit your code
# Run tests
./dev_env.sh test

# Check Django
python manage.py check
```

### 3. Database Changes
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### 4. Testing
```bash
# Run tests
./dev_env.sh test

# Check coverage
coverage run --source='.' manage.py test
coverage report
```

### 5. End of Day
```bash
# Stop server
./dev_env.sh stop

# Or just close terminal (server will stop)
```

## 🎨 Development Tips

### Code Quality
```bash
# Format code
black .

# Check code style
flake8 .

# Run all quality checks
./dev_env.sh test
```

### Debugging
```bash
# View logs
./dev_env.sh logs

# Check server status
./dev_env.sh status

# Use development dashboard
http://localhost:8000/dev/
```

### Performance
```bash
# Monitor system resources
http://localhost:8000/dev/

# Check database queries
python manage.py shell
from django.db import connection
connection.queries
```

## 🚨 Emergency Procedures

### Server Won't Start
```bash
# Check if port is in use
lsof -i :8000

# Kill all Django processes
pkill -f "python manage.py runserver"

# Restart
./dev_env.sh start
```

### Database Issues
```bash
# Check database
python manage.py check --database default

# Reset (development only)
python manage.py flush
```

### Environment Issues
```bash
# Recreate environment
conda deactivate
conda remove -n keryu --all
conda create -n keryu python=3.11
conda activate keryu
pip install -r requirements.txt
```

## 📞 Support

### Getting Help
1. Check the troubleshooting section above
2. Use the development dashboard: http://localhost:8000/dev/
3. View logs: `./dev_env.sh logs`
4. Check status: `./dev_env.sh status`

### Useful Commands
```bash
# Quick status check
./dev_env.sh status

# View all available commands
./dev_env.sh help

# Check Django configuration
python manage.py check

# View recent logs
tail -f django.log
```

---

**Happy Coding! 🎉**

For more detailed information, see:
- [Development Workflow](DEV_WORKFLOW.md)
- [Troubleshooting Guide](DEV_TROUBLESHOOTING.md)
- [API Testing Guide](DEV_API_TESTING.md) 