# Plan to Improve Nginx Startup Script

## Overview
This plan outlines the steps to improve the Nginx startup process by integrating it with systemd services, ensuring proper dependency management, automatic restarts, and better monitoring.

## Current Issues
1. Nginx startup is not properly integrated with systemd
2. No automatic dependency management
3. Limited health checking
4. Manual process management
5. No automatic restart on failure

## Implementation Steps

### 1. Create Systemd Service Files

#### 1.1 Nginx Service File
Create `/etc/systemd/system/keryu-nginx.service`:
```ini
[Unit]
Description=Keryu Nginx Service
After=network.target
Wants=network.target

[Service]
Type=forking
PIDFile=/var/run/nginx.pid
ExecStartPre=/usr/sbin/nginx -t
ExecStart=/usr/sbin/nginx
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

#### 1.2 Gunicorn Service File
Create `/etc/systemd/system/keryu-gunicorn.service`:
```ini
[Unit]
Description=Keryu Gunicorn Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/keryu3
Environment="PATH=/home/ubuntu/miniconda3/envs/keryu/bin"
ExecStart=/home/ubuntu/miniconda3/envs/keryu/bin/gunicorn \
    --workers 4 \
    --bind 0.0.0.0:8000 \
    --access-logfile /home/ubuntu/keryu3/logs/gunicorn_access.log \
    --error-logfile /home/ubuntu/keryu3/logs/gunicorn_error.log \
    --pid /tmp/gunicorn.pid \
    core.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 2. Update Startup Script

#### 2.1 Modify startup.sh
```bash
# Function to start services
start_services() {
    echo "Starting services..."
    
    # Create log directory if it doesn't exist
    mkdir -p /home/ubuntu/keryu3/logs
    
    # Start Redis
    echo "Starting Redis..."
    sudo systemctl start redis
    sleep 2
    if ! check_service redis; then
        exit 1
    fi
    echo "✓ Redis started"
    
    # Start Celery worker
    echo "Starting Celery worker..."
    sudo systemctl start keryu-celery-worker
    sleep 5
    if ! check_service keryu-celery-worker; then
        exit 1
    fi
    echo "✓ Celery worker started"
    
    # Start Celery beat
    echo "Starting Celery beat..."
    sudo systemctl start keryu-celery-beat
    sleep 3
    if ! check_service keryu-celery-beat; then
        exit 1
    fi
    echo "✓ Celery beat started"
    
    # Start Gunicorn
    echo "Starting Gunicorn..."
    sudo systemctl start keryu-gunicorn
    sleep 5
    if ! check_service keryu-gunicorn; then
        exit 1
    fi
    echo "✓ Gunicorn started"
    
    # Start Nginx
    echo "Starting Nginx..."
    sudo systemctl start keryu-nginx
    sleep 3
    if ! check_service keryu-nginx; then
        exit 1
    fi
    echo "✓ Nginx started"
}
```

### 3. Implementation Steps

1. Create systemd service files:
   ```bash
   sudo nano /etc/systemd/system/keryu-nginx.service
   sudo nano /etc/systemd/system/keryu-gunicorn.service
   sudo nano /etc/systemd/system/keryu-celery-worker.service
   sudo nano /etc/systemd/system/keryu-celery-beat.service
   ```

2. Reload systemd:
   ```bash
   sudo systemctl daemon-reload
   ```

3. Enable services:
   ```bash
   sudo systemctl enable keryu-nginx
   sudo systemctl enable keryu-gunicorn
   sudo systemctl enable keryu-celery-worker
   sudo systemctl enable keryu-celery-beat
   ```

4. Update startup.sh with new service management code

5. Test the new setup:
   ```bash
   sudo systemctl start keryu-nginx
   sudo systemctl status keryu-nginx
   ```

### 4. Testing Plan

1. Test individual service starts:
   ```bash
   sudo systemctl start keryu-nginx
   sudo systemctl status keryu-nginx
   ```

2. Test service dependencies:
   ```bash
   sudo systemctl start keryu-gunicorn
   sudo systemctl status keryu-gunicorn
   ```

3. Test full startup sequence:
   ```bash
   ./startup.sh
   ```

4. Test service recovery:
   ```bash
   sudo systemctl kill keryu-nginx
   sudo systemctl status keryu-nginx
   ```

### 5. Rollback Plan

1. Backup current configuration:
   ```bash
   sudo cp /etc/systemd/system/keryu-nginx.service /etc/systemd/system/keryu-nginx.service.bak
   ```

2. Restore original startup.sh:
   ```bash
   cp startup.sh.bak startup.sh
   ```

3. Disable new services:
   ```bash
   sudo systemctl disable keryu-nginx
   sudo systemctl disable keryu-gunicorn
   sudo systemctl disable keryu-celery-worker
   sudo systemctl disable keryu-celery-beat
   ```

## Success Criteria

1. All services start automatically on system boot
2. Services restart automatically on failure
3. Proper dependency management between services
4. Clean logging and monitoring
5. No service conflicts or port issues

## Timeline

1. Service file creation: 30 minutes
2. Script updates: 30 minutes
3. Testing: 1 hour
4. Rollback preparation: 15 minutes

Total estimated time: 2.5 hours 