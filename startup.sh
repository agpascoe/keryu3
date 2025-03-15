#!/bin/zsh

# Print colorful status messages
print_status() {
    echo -e "\033[1;34m>>> $1\033[0m"
}

print_error() {
    echo -e "\033[1;31m>>> ERROR: $1\033[0m"
}

# Function to check if a process is running on a port
check_port() {
    lsof -i :$1 > /dev/null 2>&1
    return $?
}

# Function to wait for Redis to be ready
wait_for_redis() {
    print_status "Waiting for Redis to be ready..."
    local max_attempts=30
    local attempt=1
    while ! redis-cli ping > /dev/null 2>&1; do
        if [ $attempt -ge $max_attempts ]; then
            print_error "Redis failed to become ready after $max_attempts attempts"
            return 1
        fi
        echo -n "."
        sleep 1
        attempt=$((attempt + 1))
    done
    echo
    print_status "Redis is ready"
    return 0
}

# Kill any existing processes
print_status "Cleaning up existing processes..."
pkill -f "python manage.py runserver" || true
pkill -f "celery worker" || true
sleep 2

# 1. Initialize and activate conda environment
print_status "Initializing Conda environment..."
source $HOME/miniconda3/bin/activate
conda activate keryu || { print_error "Failed to activate keryu environment"; exit 1; }

# Verify conda environment is activated
if [[ "$CONDA_DEFAULT_ENV" != "keryu" ]]; then
    print_error "Conda environment 'keryu' is not activated"
    exit 1
fi

# 2. Start Redis if not already running
print_status "Starting Redis server..."
if ! check_port 6379; then
    brew services start redis || { print_error "Failed to start Redis"; exit 1; }
    wait_for_redis || exit 1
fi

# 3. Set environment variables
export CELERY_BROKER_URL="redis://localhost:6379/0"
export CELERY_RESULT_BACKEND="redis://localhost:6379/0"
export PYTHONPATH=$PWD:$PYTHONPATH

# Start Celery worker
print_status "Starting Celery worker..."
# Generate a unique worker name using timestamp
WORKER_NAME="celery_worker_$(date +%s)"

# Start Celery worker with unique name
cd $PWD && $CONDA_PREFIX/bin/celery -A keryu3 worker -l INFO -P solo --detach -n $WORKER_NAME

# Verify Celery is running by checking Redis for worker registration
sleep 3  # Give time for worker to register
if ! redis-cli -n 0 keys "celery@*" > /dev/null 2>&1; then
    print_error "Celery worker failed to register with Redis"
    exit 1
fi
print_status "Celery worker is running with name: $WORKER_NAME"

# 4. Start Django development server
print_status "Starting Django development server..."
python manage.py runserver 