#!/bin/zsh

# Print colorful status messages
print_status() {
    echo -e "\033[1;34m>>> $1\033[0m"
}

print_error() {
    echo -e "\033[1;31m>>> ERROR: $1\033[0m"
}

# Verify single instance of a process
verify_single_instance() {
    local process_name=$1
    local expected_count=${2:-1}  # Default to 1 if not specified
    local count=$(ps aux | grep -E "$process_name" | grep -v grep | wc -l)
    
    if [ $count -gt $expected_count ]; then
        print_error "Too many instances of $process_name detected ($count instances, expected $expected_count)"
        return 1
    elif [ $count -eq 0 ]; then
        print_error "No instance of $process_name is running"
        return 1
    else
        print_status "Verified $count instance(s) of $process_name"
        return 0
    fi
}

# Kill all existing processes
print_status "Cleaning up existing processes..."
pkill -9 -f "celery worker" 
pkill -9 -f "celery beat" 
pkill -9 -f "runserver" 
brew services stop redis
sleep 2

# Initialize and activate conda environment first
print_status "Initializing Conda environment..."
# Ensure conda is initialized in zsh
source $HOME/miniconda3/etc/profile.d/conda.sh
conda activate keryu || { print_error "Failed to activate keryu environment"; exit 1; }

# Verify conda environment is activated
if [[ "$CONDA_DEFAULT_ENV" != "keryu" ]]; then
    print_error "Conda environment 'keryu' is not activated"
    exit 1
fi
print_status "Successfully activated keryu environment"

# Export the conda environment path for subprocesses
export PATH="$CONDA_PREFIX/bin:$PATH"

# Start Redis
print_status "Starting Redis server..."
brew services start redis || { print_error "Failed to start Redis"; exit 1; }
sleep 2

# Wait for Redis to be ready
print_status "Waiting for Redis to be ready..."
max_attempts=30
attempt=1
while ! redis-cli ping > /dev/null 2>&1; do
    if [ $attempt -ge $max_attempts ]; then
        print_error "Redis failed to become ready after $max_attempts attempts"
        exit 1
    fi
    echo -n "."
    sleep 1
    attempt=$((attempt + 1))
done
echo
print_status "Redis is ready"

# Set environment variables
export CELERY_BROKER_URL="redis://localhost:6379/0"
export CELERY_RESULT_BACKEND="redis://localhost:6379/0"
export PYTHONPATH=$PWD:$PYTHONPATH

# Start Celery worker (single instance)
print_status "Starting Celery worker..."
WORKER_NAME="keryu_worker_$(date +%s)"
$CONDA_PREFIX/bin/celery -A keryu3 worker -l INFO -P solo -Q subjects,alarms,default --hostname=$WORKER_NAME --purge --without-mingle --without-gossip &
WORKER_PID=$!

# Wait for worker to start
sleep 10
if ! ps -p $WORKER_PID > /dev/null; then
    print_error "Celery worker failed to start"
    exit 1
fi
print_status "Celery worker is running with name: $WORKER_NAME"

# Start Celery beat scheduler (single instance)
print_status "Starting Celery beat scheduler..."
$CONDA_PREFIX/bin/celery -A keryu3 beat -l INFO &
BEAT_PID=$!

# Wait for beat to start
sleep 10
if ! ps -p $BEAT_PID > /dev/null; then
    print_error "Celery beat scheduler failed to start"
    exit 1
fi
print_status "Celery beat scheduler is running"

# Start Django development server
print_status "Starting Django development server..."
# Kill any existing Django servers first
pkill -f "manage.py runserver"
sleep 2

# Start the Django server (will auto-spawn second process for reloader)
$CONDA_PREFIX/bin/python manage.py runserver > django.log 2>&1 &
DJANGO_PID=$!

# Wait for Django to start and verify it's running properly
print_status "Waiting for Django server to start..."
max_attempts=30
attempt=1
while ! curl -s http://127.0.0.1:8000 > /dev/null 2>&1; do
    if [ $attempt -ge $max_attempts ]; then
        print_error "Django server failed to start after $max_attempts attempts"
        cat django.log
        exit 1
    fi
    if ! ps -p $DJANGO_PID > /dev/null; then
        print_error "Django server process died"
        cat django.log
        exit 1
    fi
    echo -n "."
    sleep 1
    attempt=$((attempt + 1))
done
echo
print_status "Django server is running"

# Verify single instances with more precise matching
print_status "Verifying single instances of all services..."
verify_single_instance "/usr/local/opt/redis/bin/redis-server"
verify_single_instance "celery -A keryu3 worker.*--hostname=$WORKER_NAME"
verify_single_instance "celery -A keryu3 beat"
verify_single_instance "manage.py runserver" 2  # Allow 2 processes for Django

print_status "All services are running with expected number of instances"
print_status "System is ready for testing"

# Keep the script running and clean up on exit
trap "pkill -f 'celery worker' && pkill -f 'celery beat' && pkill -f 'runserver' && rm django.log" EXIT
wait $DJANGO_PID 