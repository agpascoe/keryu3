#!/bin/bash

# Exit on error
set -e

# Trap errors only, remove the EXIT trap
trap 'handle_error $? $LINENO' ERR

echo "Starting Keryu services startup sequence..."

# Global variables for process tracking
declare -A PIDS
declare -A PROCESS_STATES

# Activate conda environment
source /home/ubuntu/miniconda3/etc/profile.d/conda.sh
conda activate keryu

# Function to handle errors
handle_error() {
    local exit_code=$1
    local line_no=$2
    echo "Error occurred in line $line_no with exit code $exit_code"
    cleanup
    exit $exit_code
}

# Function to cleanup processes
cleanup() {
    echo "Cleaning up processes..."
    for pid in "${!PIDS[@]}"; do
        if [ -n "${PIDS[$pid]}" ] && kill -0 "${PIDS[$pid]}" 2>/dev/null; then
            echo "Stopping process $pid (${PIDS[$pid]})"
            kill "${PIDS[$pid]}" 2>/dev/null || true
            wait "${PIDS[$pid]}" 2>/dev/null || true
        fi
    done
}

# Function to check if a service is running
is_service_running() {
    local service=$1
    systemctl is-active --quiet "$service"
    return $?
}

# Function to check if a process is running
check_process() {
    local pattern=$1
    local count=$(pgrep -f "$pattern" | wc -l)
    return $(( count == 0 ))
}

# Function to check if port is in use
check_port() {
    local port=$1
    ss -tuln | grep -q ":$port "
    return $?
}

# Function to wait for port to be available
wait_for_port() {
    local port=$1
    local max_attempts=30
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

# Function to check service status
check_service() {
    local service=$1
    if ! systemctl is-active --quiet "$service"; then
        echo "✗ Failed to start $service"
        sudo journalctl -u "$service" --no-pager | tail -n 10
        return 1
    fi
    return 0
}

# Function to gracefully stop services
stop_services() {
    echo "Stopping services..."
    
    # Stop Nginx if running
    if is_service_running nginx; then
        echo "Stopping Nginx..."
        sudo systemctl stop nginx
        sleep 2
    fi
    
    # Stop Redis if running
    if is_service_running redis; then
        echo "Stopping Redis..."
        sudo systemctl stop redis
        sleep 2
    fi
    
    # Stop application processes
    echo "Stopping application processes..."
    
    # Kill all child processes first
    for pid in "${!PIDS[@]}"; do
        if [ -n "${PIDS[$pid]}" ]; then
            echo "Stopping $pid process..."
            kill "${PIDS[$pid]}" 2>/dev/null || true
            wait "${PIDS[$pid]}" 2>/dev/null || true
        fi
    done
    
    # Kill any remaining processes
    pkill -f "celery worker" || true
    pkill -f "celery beat" || true
    pkill -f "gunicorn" || true
    pkill -f "runserver" || true
    
    # Wait for processes to die
    sleep 2
    
    # Verify processes are stopped
    if pgrep -f "celery|gunicorn" > /dev/null; then
        echo "! Warning: Some processes still running, forcing kill..."
        pkill -9 -f "celery|gunicorn" || true
    fi
}

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
    cd /home/ubuntu/keryu3
    bash -c 'source /home/ubuntu/miniconda3/etc/profile.d/conda.sh && conda activate keryu && celery -A core worker --loglevel=info > logs/celery_worker.log 2>&1' &
    PIDS["celery_worker"]=$!
    sleep 5
    if ! grep -q "celery@.*ready" logs/celery_worker.log; then
        echo "✗ Failed to start Celery worker"
        cat logs/celery_worker.log
        exit 1
    fi
    echo "✓ Celery worker started"
    
    # Start Celery beat
    echo "Starting Celery beat..."
    bash -c 'source /home/ubuntu/miniconda3/etc/profile.d/conda.sh && conda activate keryu && celery -A core beat --loglevel=info > logs/celery_beat.log 2>&1' &
    PIDS["celery_beat"]=$!
    sleep 3
    if ! check_process "celery.*beat"; then
        echo "✗ Failed to start Celery beat"
        cat logs/celery_beat.log
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
    cd /home/ubuntu/keryu3
    
    # Kill any existing Gunicorn processes
    if [ -f /tmp/gunicorn.pid ]; then
        pid=$(cat /tmp/gunicorn.pid)
        kill -9 $pid 2>/dev/null || true
        rm -f /tmp/gunicorn.pid
    fi
    pkill -f "gunicorn" || true
    
    # Start Gunicorn with proper environment
    source /home/ubuntu/miniconda3/etc/profile.d/conda.sh
    conda activate keryu
    
    # Clear log files
    > logs/gunicorn_error.log
    > logs/gunicorn_access.log
    
    # Start Gunicorn
    gunicorn core.wsgi:application \
        --workers 4 \
        --bind 0.0.0.0:8000 \
        --access-logfile logs/gunicorn_access.log \
        --error-logfile logs/gunicorn_error.log \
        --pid /tmp/gunicorn.pid \
        --daemon
    
    # Wait for PID file to be created
    max_attempts=10
    attempt=1
    while [ $attempt -le $max_attempts ]; do
        if [ -f /tmp/gunicorn.pid ]; then
            PIDS["gunicorn"]=$(cat /tmp/gunicorn.pid)
            break
        fi
        echo "Waiting for Gunicorn PID file... (attempt $attempt/$max_attempts)"
        sleep 1
        attempt=$((attempt + 1))
    done
    
    if [ ! -f /tmp/gunicorn.pid ]; then
        echo "✗ Failed to create Gunicorn PID file"
        cat logs/gunicorn_error.log
        exit 1
    fi
    
    # Wait for Gunicorn to start
    sleep 5
    if ! check_process "gunicorn"; then
        echo "✗ Failed to start Gunicorn"
        cat logs/gunicorn_error.log
        exit 1
    fi
    echo "✓ Gunicorn started"
    
    # Start Nginx
    echo "Starting Nginx..."
    sudo systemctl start nginx
    sleep 3
    if ! check_service nginx; then
        echo "✗ Failed to start Nginx"
        sudo journalctl -u nginx --no-pager | tail -n 10
        exit 1
    fi
    echo "✓ Nginx started"
}

# Function to verify services
verify_services() {
    echo -e "\nVerifying all processes..."
    failed=0
    
    # Check processes
    if ! grep -q "celery@.*ready" logs/celery_worker.log; then
        echo "! Warning: Celery worker not running properly"
        failed=1
    fi
    
    if ! check_process "celery.*beat"; then
        echo "! Warning: Celery beat not running"
        failed=1
    fi
    
    # Check gunicorn processes
    if [ ! -f /tmp/gunicorn.pid ]; then
        echo "! Warning: Gunicorn PID file not found"
        failed=1
    else
        gunicorn_pid=$(cat /tmp/gunicorn.pid)
        if ! ps -p $gunicorn_pid > /dev/null; then
            echo "! Warning: Gunicorn master process not running"
            failed=1
        else
            worker_count=$(pgrep -P $gunicorn_pid | wc -l)
            if [ "$worker_count" -ne 4 ]; then
                echo "! Warning: Gunicorn not running with correct number of workers (expected 4, got $worker_count)"
                failed=1
            fi
        fi
    fi
    
    # Check services
    if ! check_service nginx; then
        echo "! Warning: Nginx not running"
        failed=1
    fi
    
    if ! check_service redis; then
        echo "! Warning: Redis not running"
        failed=1
    fi
    
    # Check port 8000 through Nginx
    echo "Checking application response..."
    max_attempts=30
    attempt=1
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost/ > /dev/null; then
            echo "✓ Application responding correctly"
            break
        fi
        echo "Waiting for application to respond... (attempt $attempt/$max_attempts)"
        sleep 1
        attempt=$((attempt + 1))
    done
    if [ $attempt -gt $max_attempts ]; then
        echo "✗ Application failed to respond"
        echo "Checking Nginx configuration..."
        sudo nginx -t
        echo "Checking Nginx error log..."
        sudo tail -n 50 /var/log/nginx/error.log
        exit 1
    fi
    
    if [ $failed -eq 1 ]; then
        echo -e "\n✗ Some services failed to start properly"
        exit 1
    fi
}

# Main script
case "$1" in
    "stop")
        echo "Stopping all services..."
        stop_services
        echo "✓ All services stopped"
        ;;
    "restart")
        echo "Restarting all services..."
        stop_services
        sleep 2
        start_services
        verify_services
        ;;
    "start"|"")
        echo "Starting services..."
        start_services
        verify_services
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac 