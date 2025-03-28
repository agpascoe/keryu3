# Keryu AWS EC2 Deployment Guide - Plan A

## Prerequisites
- AWS Account with EC2 access
- Domain name (optional, but recommended)
- Meta WhatsApp Business API credentials
- Twilio credentials (for fallback)

## 1. EC2 Instance Setup
```bash
# Instance Recommendations
- Ubuntu Server 22.04 LTS
- t2.small minimum (2GB RAM)
- 20GB EBS volume
```

### Security Group Configuration
```
Inbound Rules:
- SSH (Port 22) from your IP
- HTTP (Port 80) from anywhere
- HTTPS (Port 443) from anywhere
- Custom TCP (Port 8000) for development (optional)
```

## 2. Initial Server Setup
```bash
# Connect to your instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update
sudo apt upgrade -y

# Install required system packages
sudo apt install -y python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx curl build-essential git

# Install Redis
sudo apt install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Verify Redis is running
sudo systemctl status redis
```

## 3. PostgreSQL Setup
```bash
# Create database and user
sudo -u postgres psql

postgres=# CREATE DATABASE keryu;
postgres=# CREATE USER keryu_user WITH PASSWORD 'your_secure_password';
postgres=# ALTER ROLE keryu_user SET client_encoding TO 'utf8';
postgres=# ALTER ROLE keryu_user SET default_transaction_isolation TO 'read committed';
postgres=# ALTER ROLE keryu_user SET timezone TO 'UTC';
postgres=# GRANT ALL PRIVILEGES ON DATABASE keryu TO keryu_user;
postgres=# \q
```

## 4. Application Setup
```bash
# Create application directory
sudo mkdir /var/www/keryu
sudo chown ubuntu:ubuntu /var/www/keryu

# Clone repository
cd /var/www/keryu
git clone https://your-repo-url.git .

# Create virtual environment
sudo apt install -y python3-venv
python3 -m venv venv
source venv/bin/activate

# Install base dependencies
pip install setuptools  # Required for pkg_resources
pip install wheel  # Required for some packages

# Install project dependencies
pip install -r requirements.txt

# Install additional required packages
pip install drf-yasg  # For API documentation
```

## 5. Environment Configuration
```bash
# Create .env file
nano .env

# Generate a new SECRET_KEY using Python
python3 -c "import secrets; print(secrets.token_urlsafe(50))"

# Add environment variables to .env
DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-ip-address
SECRET_KEY=your-generated-secret-key
DB_NAME=keryu
DB_USER=keryu_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# WhatsApp API Configuration
WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id

# Twilio Configuration (Fallback)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_phone_number
TWILIO_WHATSAPP_NUMBER=your_whatsapp_number

# Redis Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## 6. Gunicorn Setup
```bash
# Install Gunicorn
pip install gunicorn

# Create Gunicorn systemd service
sudo nano /etc/systemd/system/gunicorn.service

[Unit]
Description=Gunicorn daemon for Keryu
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/keryu
Environment="DJANGO_SETTINGS_MODULE=keryu3.settings"
Environment="PYTHONPATH=/var/www/keryu:/var/www/keryu/keryu3"
ExecStart=/var/www/keryu/venv/bin/gunicorn \
    --access-logfile - \
    --error-logfile - \
    --workers 3 \
    --bind unix:/var/www/keryu/keryu.sock \
    keryu3.wsgi:application

[Install]
WantedBy=multi-user.target

# Create directory for the socket file if it doesn't exist
sudo mkdir -p /var/www/keryu
sudo chown ubuntu:www-data /var/www/keryu

# Set proper permissions
sudo chmod 644 /etc/systemd/system/gunicorn.service

# Create wsgi.py if it doesn't exist
nano keryu3/wsgi.py

# Add this content to wsgi.py
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'keryu3.settings')
application = get_wsgi_application()

# Reload systemd and start Gunicorn
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn

# Verify Gunicorn is running
sudo systemctl status gunicorn
```

## 7. Celery Setup
```bash
# First, verify Redis is running
sudo systemctl status redis

# Install Celery dependencies
pip install "celery[redis]"
pip install django-celery-beat

# Create Celery worker service
sudo nano /etc/systemd/system/celery.service

[Unit]
Description=Celery Worker for Keryu
After=network.target redis.service

[Service]
Type=simple
User=ubuntu
Group=www-data
EnvironmentFile=/var/www/keryu/.env
WorkingDirectory=/var/www/keryu
Environment="DJANGO_SETTINGS_MODULE=keryu3.settings"
Environment="PYTHONPATH=/var/www/keryu:/var/www/keryu/keryu3"
ExecStart=/var/www/keryu/venv/bin/celery -A keryu3 worker --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target

# Create Celery Beat service
sudo nano /etc/systemd/system/celerybeat.service

[Unit]
Description=Celery Beat for Keryu
After=network.target redis.service celery.service

[Service]
Type=simple
User=ubuntu
Group=www-data
EnvironmentFile=/var/www/keryu/.env
WorkingDirectory=/var/www/keryu
Environment="DJANGO_SETTINGS_MODULE=keryu3.settings"
Environment="PYTHONPATH=/var/www/keryu:/var/www/keryu/keryu3"
ExecStart=/var/www/keryu/venv/bin/celery -A keryu3 beat --loglevel=info
Restart=always

[Install]
WantedBy=multi-user.target

# Set proper permissions for both service files
sudo chmod 644 /etc/systemd/system/celery.service
sudo chmod 644 /etc/systemd/system/celerybeat.service

# Reload systemd and start services
sudo systemctl daemon-reload
sudo systemctl start celery
sudo systemctl enable celery
sudo systemctl start celerybeat
sudo systemctl enable celerybeat

# Verify services are running
sudo systemctl status celery
sudo systemctl status celerybeat

# If services fail, check logs
sudo journalctl -u celery -n 50
sudo journalctl -u celerybeat -n 50
```

## 8. Nginx Setup
```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/keryu

server {
    listen 80;
    server_name your-domain.com;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }
    
    location /static/ {
        root /var/www/keryu;
    }

    location /media/ {
        root /var/www/keryu;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/keryu/keryu.sock;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# Create symbolic link
sudo ln -s /etc/nginx/sites-available/keryu /etc/nginx/sites-enabled/

# Remove default nginx site if exists
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

## 9. SSL Configuration (Let's Encrypt)
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Stop nginx temporarily
sudo systemctl stop nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Verify auto-renewal
sudo systemctl status certbot.timer

# Start nginx
sudo systemctl start nginx
```

## 10. Django Setup
```bash
# Collect static files
python manage.py collectstatic --noinput

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Test the Django installation
python manage.py check --deploy
```

## 11. Service Verification and Troubleshooting
```bash
# Verify all services are running
sudo systemctl status nginx
sudo systemctl status gunicorn
sudo systemctl status redis
sudo systemctl status celery
sudo systemctl status celerybeat

# Check if services are properly enabled
systemctl is-enabled gunicorn
systemctl is-enabled celery
systemctl is-enabled celerybeat

# Check service logs
sudo journalctl -u gunicorn
sudo journalctl -u celery
sudo journalctl -u celerybeat
sudo tail -f /var/log/nginx/error.log

# Check socket file
ls -l /var/www/keryu/keryu.sock
```

## 12. Security Setup
```bash
# Configure UFW (Uncomplicated Firewall)
sudo ufw allow 'Nginx Full'
sudo ufw allow ssh
sudo ufw enable

# Verify UFW status
sudo ufw status

# Secure PostgreSQL (if needed)
sudo nano /etc/postgresql/14/main/pg_hba.conf
sudo systemctl restart postgresql
```

## 13. Maintenance Commands
```bash
# Restart all services
sudo systemctl restart nginx gunicorn celery celerybeat redis

# View logs
sudo journalctl -xe  # For system logs
sudo journalctl -u gunicorn  # For Gunicorn logs
sudo journalctl -u celery  # For Celery logs
sudo journalctl -u celerybeat  # For Celery Beat logs
sudo tail -f /var/log/nginx/error.log  # For Nginx error logs
```

## 14. Backup Setup
```bash
# Create backup directory
sudo mkdir -p /var/backups/keryu

# Set up PostgreSQL backup script
sudo nano /etc/cron.daily/backup-keryu-db

#!/bin/bash
BACKUP_DIR="/var/backups/keryu"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
pg_dump keryu > "$BACKUP_DIR/keryu_$TIMESTAMP.sql"
find "$BACKUP_DIR" -type f -mtime +7 -delete

# Make backup script executable
sudo chmod +x /etc/cron.daily/backup-keryu-db
```

## 15. Post-Deployment Checks
```bash
# Check Django deployment settings
python manage.py check --deploy

# Test WhatsApp integration
python manage.py test notifications.tests

# Monitor system resources
htop  # Install if needed: sudo apt install htop

# Check logs for any errors
sudo tail -f /var/log/nginx/error.log
sudo journalctl -f
```

## Important Notes
1. Always keep your `.env` file secure and never commit it to version control
2. Regularly update your SSL certificates
3. Monitor your logs for any errors or suspicious activity
4. Keep regular backups of your database and media files
5. Update your system and dependencies regularly
6. Monitor system resources (CPU, memory, disk space)

## Troubleshooting Common Issues

### If Gunicorn fails to start:
```bash
# Check Gunicorn logs
sudo journalctl -u gunicorn -n 50
# Verify PYTHONPATH
echo $PYTHONPATH
# Check wsgi.py exists and is correct
cat keryu3/wsgi.py
```

### If Celery fails to start:
```bash
# Check Redis is running
sudo systemctl status redis
# Check Celery logs
sudo journalctl -u celery -n 50
# Try running Celery manually
celery -A keryu3 worker --loglevel=info
```

### If Nginx returns 502 Bad Gateway:
```bash
# Check Gunicorn socket
ls -l /var/www/keryu/keryu.sock
# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
# Verify Nginx configuration
sudo nginx -t
```

## Scaling Considerations
1. Consider using AWS RDS for PostgreSQL
2. Set up AWS ElastiCache for Redis
3. Use AWS S3 for media file storage
4. Implement AWS CloudWatch for monitoring
5. Consider using AWS ELB for load balancing

## Security Best Practices
1. Keep all packages updated
2. Use strong passwords
3. Regularly rotate API keys
4. Monitor access logs
5. Set up fail2ban
6. Configure regular security updates
7. Use AWS security groups effectively
8. Implement rate limiting
9. Set up monitoring and alerting

## Monitoring Setup
1. Set up AWS CloudWatch
2. Configure log rotation
3. Set up error alerting
4. Monitor system resources
5. Track application metrics

## Backup Strategy
1. Daily database backups
2. Regular media file backups
3. Configuration backups
4. Automated cleanup of old backups
5. Test restore procedures regularly 