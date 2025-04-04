#!/bin/bash

echo "Starting Keryu services startup sequence..."

# Kill any existing processes first
echo "Cleaning up existing processes..."
sudo pkill -f "celery worker" || true
sudo pkill -f "celery beat" || true
sudo pkill -f "gunicorn" || true
sudo pkill -f "runserver" || true
sleep 2

# Stop services first
echo "Stopping services..."
sudo systemctl stop nginx || true
sudo systemctl stop redis || true
sleep 2

# Function to check if port is in use
check_port() {
    local port=$1
    ss -tuln | grep -q ":$port "
    return $?
}

# Function to wait for port to be available
wait_for_port() {
    local port=$1
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if ! check_port "$port"; then
        return 0
    fi
        echo "Port $port is still in use, waiting... (attempt $attempt/$max_attempts)"
        sleep 1
        attempt=$((attempt + 1))
    done
    return 1
}

# Function to check if a process is running
check_process() {
    local pattern=$1
    local count=$(pgrep -f "$pattern" | wc -l)
    return $(( count == 0 ))
}

# Start Redis
echo "Starting Redis..."
sudo systemctl start redis
sleep 2
if ! systemctl is-active --quiet redis; then
    echo "✗ Failed to start Redis"
    exit 1
fi
echo "✓ Redis started"

# Start Celery worker
echo "Starting Celery worker..."
cd /home/ubuntu/keryu3
celery -A core worker --loglevel=info > celery_worker.log 2>&1 &
sleep 5
if ! grep -q "celery@.*ready" celery_worker.log; then
    echo "✗ Failed to start Celery worker"
    cat celery_worker.log
    exit 1
fi
echo "✓ Celery worker started"

# Start Celery beat
echo "Starting Celery beat..."
celery -A core beat --loglevel=info > celery_beat.log 2>&1 &
sleep 3
if ! check_process "celery.*beat"; then
    echo "✗ Failed to start Celery beat"
    cat celery_beat.log
    exit 1
fi
echo "✓ Celery beat started"

# Wait for port 8000 to be available
echo "Checking port 8000..."
if ! wait_for_port 8000; then
    echo "✗ Port 8000 is still in use"
    exit 1
fi

# Start Gunicorn
echo "Starting Gunicorn..."
gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3 --access-logfile gunicorn_access.log --error-logfile gunicorn_error.log --daemon
sleep 3
if ! check_process "gunicorn"; then
    echo "✗ Failed to start Gunicorn"
    cat gunicorn_error.log
    exit 1
fi
echo "✓ Gunicorn started"

# Start Nginx last
echo "Starting Nginx..."
sudo systemctl start nginx
sleep 2
if ! systemctl is-active --quiet nginx; then
    echo "✗ Failed to start Nginx"
    sudo journalctl -u nginx --no-pager | tail -n 10
    exit 1
fi
echo "✓ Nginx started"

# Final verification
echo -e "\nVerifying all processes..."
failed=0

# Check processes
if ! grep -q "celery@.*ready" celery_worker.log; then
    echo "! Warning: Celery worker not running properly"
    failed=1
fi

if ! check_process "celery.*beat"; then
    echo "! Warning: Celery beat not running"
    failed=1
fi

if ! check_process "gunicorn"; then
    echo "! Warning: Gunicorn not running"
    failed=1
fi

# Check services
if ! systemctl is-active --quiet nginx; then
    echo "! Warning: Nginx not running"
    failed=1
fi

if ! systemctl is-active --quiet redis; then
    echo "! Warning: Redis not running"
    failed=1
fi

# Check port 8000 through Nginx
echo "Checking application response..."
if ! curl -s -I http://localhost/ | grep -q "200 OK\|301 Moved Permanently"; then
    echo "! Warning: Application not responding through Nginx"
    failed=1
else
    echo "✓ Application responding correctly"
fi

if [ $failed -eq 1 ]; then
    echo -e "\n✗ Some services failed to start properly"
    exit 1
fi

echo -e "\n✓ All services and processes successfully started"
echo "You can monitor the logs using:"
echo "- Celery Worker: tail -f celery_worker.log"
echo "- Celery Beat: tail -f celery_beat.log"
echo "- Gunicorn Access: tail -f gunicorn_access.log"
echo "- Gunicorn Error: tail -f gunicorn_error.log"
echo "- Nginx: sudo journalctl -f -u nginx"
echo "- Redis: sudo journalctl -f -u redis"

# Show current status
echo -e "\nCurrent process status:"
ps aux | grep -E "celery|gunicorn|nginx" | grep -v grep 