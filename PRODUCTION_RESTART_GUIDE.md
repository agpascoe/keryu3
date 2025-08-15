# Keryu Production Restart Guide

## Overview
This guide provides complete steps to restart the Keryu production website at https://keryu.mx from scratch. Follow these steps in order to ensure a successful deployment.

## Prerequisites
- Ubuntu server with sudo access
- Python 3.11+ and Conda installed
- PostgreSQL database configured
- Domain name (keryu.mx) pointing to server
- SSL certificates (Let's Encrypt) configured
- Meta WhatsApp Business API access

## Step 1: Environment Setup

### 1.1 Navigate to Project Directory
```bash
cd /home/ubuntu/keryu3
```

### 1.2 Activate Conda Environment
```bash
source /home/ubuntu/miniconda3/etc/profile.d/conda.sh
conda activate keryu
```

### 1.3 Verify Environment
```bash
python --version  # Should be 3.11+
which python     # Should point to conda environment
```

## Step 2: Stop Any Existing Services

### 2.1 Stop Development Server (if running)
```bash
./dev_env.sh stop
```

### 2.2 Stop Production Services
```bash
# Stop Nginx
sudo systemctl stop nginx

# Stop Redis
sudo systemctl stop redis

# Kill any remaining processes
pkill -f "gunicorn" || true
pkill -f "celery" || true
pkill -f "runserver" || true

# Wait for processes to die
sleep 3
```

### 2.3 Verify No Conflicting Processes
```bash
ps aux | grep -E "(gunicorn|celery|runserver)" | grep -v grep
# Should return no results
```

## Step 3: Environment Validation

### 3.1 Check Django Configuration
```bash
python manage.py check --deploy
```

### 3.2 Verify SSL Certificates
```bash
sudo certbot certificates
# Should show valid certificates for keryu.mx
```

### 3.3 Test Database Connection
```bash
python manage.py check --database default
```

### 3.4 Verify Dependencies
```bash
pip list | grep -E "(Django|celery|redis|gunicorn)"
```

## Step 4: Prepare Production Environment

### 4.1 Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 4.2 Set Proper Permissions
```bash
sudo chown -R ubuntu:ubuntu /home/ubuntu/keryu3
chmod +x startup.sh
```

### 4.3 Create Log Directory
```bash
mkdir -p logs
chmod 755 logs
```

## Step 5: Start Production Services

### 5.1 Start All Services
```bash
./startup.sh start
```

This command will automatically:
- Start Redis server
- Start Celery worker
- Start Celery beat scheduler
- Start Gunicorn with 4 workers
- Start Nginx with SSL configuration
- Verify all services are running

### 5.2 Monitor Startup Process
The startup script will show progress:
```
Starting Keryu services startup sequence...
Starting services...
Starting Redis...
✓ Redis started
Starting Celery worker...
✓ Celery worker started
Starting Celery beat...
✓ Celery beat started
Starting Gunicorn...
✓ Gunicorn started
Starting Nginx...
✓ Nginx started
Verifying all processes...
✓ Application responding correctly
```

## Step 6: Verify Production Deployment

### 6.1 Check Service Status
```bash
# Check Nginx
sudo systemctl status nginx

# Check Redis
sudo systemctl status redis

# Check running processes
ps aux | grep -E "(gunicorn|celery)" | grep -v grep
```

### 6.2 Test HTTPS Access
```bash
# Test main domain
curl -I https://keryu.mx

# Test with content
curl -s https://keryu.mx | head -5
```

### 6.3 Verify SSL Certificate
```bash
# Check certificate validity
openssl s_client -connect keryu.mx:443 -servername keryu.mx < /dev/null
```

### 6.4 Check Log Files
```bash
# View recent logs
ls -la logs/
tail -10 logs/gunicorn_error.log
tail -10 logs/celery_worker.log
```

## Step 7: Final Verification

### 7.1 Test Core Functionality
```bash
# Test application response
curl -s https://keryu.mx | grep -i "keryu"

# Test API endpoints (if applicable)
curl -s https://keryu.mx/api/ | head -5
```

### 7.2 Check Background Services
```bash
# Verify Celery workers
ps aux | grep "celery worker" | grep -v grep

# Verify Celery beat
ps aux | grep "celery beat" | grep -v grep

# Check Redis connection
redis-cli ping
```

## Troubleshooting

### If Services Fail to Start

#### Nginx Issues
```bash
# Check Nginx configuration
sudo nginx -t

# View Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Restart Nginx
sudo systemctl restart nginx
```

#### Gunicorn Issues
```bash
# Check Gunicorn logs
tail -f logs/gunicorn_error.log

# Restart Gunicorn manually
pkill -f gunicorn
cd /home/ubuntu/keryu3
source /home/ubuntu/miniconda3/etc/profile.d/conda.sh
conda activate keryu
gunicorn core.wsgi:application --workers 4 --bind 0.0.0.0:8000 --daemon
```

#### Celery Issues
```bash
# Check Celery logs
tail -f logs/celery_worker.log
tail -f logs/celery_beat.log

# Restart Celery manually
pkill -f "celery worker"
pkill -f "celery beat"
cd /home/ubuntu/keryu3
source /home/ubuntu/miniconda3/etc/profile.d/conda.sh
conda activate keryu
celery -A core worker --loglevel=info > logs/celery_worker.log 2>&1 &
celery -A core beat --loglevel=info > logs/celery_beat.log 2>&1 &
```

### If SSL Certificate Issues
```bash
# Renew certificates
sudo certbot renew

# Check certificate status
sudo certbot certificates
```

## Quick Restart Commands

### Full Restart
```bash
cd /home/ubuntu/keryu3
./startup.sh restart
```

### Stop All Services
```bash
cd /home/ubuntu/keryu3
./startup.sh stop
```

### Start All Services
```bash
cd /home/ubuntu/keryu3
./startup.sh start
```

## Success Indicators

✅ **All services running:**
- Nginx: `active (running)`
- Redis: `active (running)`
- Gunicorn: 4 worker processes
- Celery worker: 1 process
- Celery beat: 1 process

✅ **HTTPS accessible:**
- `curl -I https://keryu.mx` returns HTTP/2 200

✅ **SSL certificate valid:**
- Certificate expires in >30 days
- No SSL errors in browser

✅ **Application responding:**
- Main page loads correctly
- No error logs in production services

✅ **Background tasks working:**
- Celery worker processing tasks
- Celery beat scheduling tasks
- Redis responding to ping

## Emergency Rollback

If production deployment fails:

```bash
# Stop production services
./startup.sh stop

# Restart development server
./dev_env.sh start

# Investigate issues
tail -f logs/gunicorn_error.log
tail -f logs/celery_worker.log
sudo journalctl -u nginx -f
```

## Maintenance Commands

### View Logs
```bash
# Application logs
tail -f logs/gunicorn_error.log
tail -f logs/gunicorn_access.log

# Background task logs
tail -f logs/celery_worker.log
tail -f logs/celery_beat.log

# System logs
sudo journalctl -u nginx -f
sudo journalctl -u redis -f
```

### Monitor Resources
```bash
# Check memory usage
free -h

# Check disk space
df -h

# Check running processes
htop
```

### Backup Database
```bash
# Create database backup
pg_dump keryu_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

## Notes

- **Environment**: Always use conda environment `keryu`
- **Working Directory**: Always run commands from `/home/ubuntu/keryu3`
- **Permissions**: Ensure proper file ownership and permissions
- **Logs**: Monitor logs for any errors or warnings
- **SSL**: Certificates auto-renew with Let's Encrypt
- **Backup**: Regular database backups recommended

## Support

If issues persist:
1. Check all log files for errors
2. Verify all prerequisites are met
3. Test each service individually
4. Review system resources
5. Check network connectivity 