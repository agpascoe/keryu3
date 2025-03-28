#!/bin/zsh

# Print colorful status messages
print_status() {
    echo -e "\033[1;34m>>> $1\033[0m"
}

print_error() {
    echo -e "\033[1;31m>>> ERROR: $1\033[0m"
}

print_debug() {
    echo -e "\033[1;33m>>> DEBUG: $1\033[0m"
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

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    print_error "Conda is not installed. Please install Miniconda or Anaconda first."
    exit 1
fi

# Check if Redis is installed
if ! command -v redis-cli &> /dev/null; then
    print_error "Redis is not installed. Please install Redis first (brew install redis)"
    exit 1
fi

# Kill all existing processes
print_status "Cleaning up existing processes..."
pkill -9 -f "celery worker" 
pkill -9 -f "celery beat" 
pkill -9 -f "runserver" 
brew services stop redis
sleep 2

# Initialize conda for the current shell
print_status "Initializing conda..."
CONDA_SH="$HOME/miniconda3/etc/profile.d/conda.sh"
if [[ ! -f "$CONDA_SH" ]]; then
    CONDA_SH="/usr/local/miniconda3/etc/profile.d/conda.sh"
fi

if [[ ! -f "$CONDA_SH" ]]; then
    print_error "Could not find conda.sh. Please ensure Conda is properly installed."
    exit 1
fi

# Source conda.sh and activate environment in a subshell to ensure it's properly activated
if ! (source "$CONDA_SH" && conda activate keryu && which celery > /dev/null); then
    print_error "Failed to activate conda environment or celery not found"
    exit 1
fi

# Set the absolute path to the conda environment
CONDA_ENV_PATH="$HOME/miniconda3/envs/keryu"
if [[ ! -d "$CONDA_ENV_PATH" ]]; then
    CONDA_ENV_PATH="/usr/local/miniconda3/envs/keryu"
fi

if [[ ! -d "$CONDA_ENV_PATH" ]]; then
    print_error "Could not find conda environment directory"
    exit 1
fi

# Set absolute paths for binaries
CELERY_BIN="$CONDA_ENV_PATH/bin/celery"
PYTHON_BIN="$CONDA_ENV_PATH/bin/python"

# Verify celery is available
if [[ ! -x "$CELERY_BIN" ]]; then
    print_error "Celery executable not found at $CELERY_BIN"
    exit 1
fi

# Verify all required packages are installed
print_status "Verifying required packages..."
required_packages=(
    "django"
    "celery"
    "redis"
    "psycopg2"
)

for package in "${required_packages[@]}"; do
    if ! python -c "import $package" &> /dev/null; then
        print_error "Required package '$package' is not installed"
        exit 1
    fi
done

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

# Create a log file for celery worker
WORKER_LOG="celery_worker.log"
touch $WORKER_LOG

print_debug "Starting worker with name: $WORKER_NAME"
print_debug "Using celery binary: $CELERY_BIN"
print_debug "Worker log file: $WORKER_LOG"

(
    source "$CONDA_SH" && \
    conda activate keryu && \
    $CELERY_BIN -A keryu3 worker \
        -l INFO \
        -P solo \
        -Q subjects,alarms,default \
        --hostname=$WORKER_NAME \
        --purge \
        --without-mingle \
        --without-gossip > $WORKER_LOG 2>&1
) &
WORKER_PID=$!

# Wait for worker to start and verify it's running
print_status "Waiting for worker to start..."
sleep 5

if ! ps -p $WORKER_PID > /dev/null; then
    print_error "Celery worker failed to start"
    print_debug "Worker log contents:"
    cat $WORKER_LOG
    exit 1
fi

# Try multiple times to check worker status
max_attempts=30
attempt=1
while ! $CELERY_BIN -A keryu3 status | grep -q "keryu_worker"; do
    if [ $attempt -ge $max_attempts ]; then
        print_error "Celery worker failed to respond after $max_attempts attempts"
        print_debug "Worker log contents:"
        cat $WORKER_LOG
        exit 1
    fi
    echo -n "."
    sleep 1
    attempt=$((attempt + 1))
done

print_status "Celery worker is running with name: $WORKER_NAME"

# Start Celery beat scheduler (single instance)
print_status "Starting Celery beat scheduler..."

# Create a log file for celery beat
BEAT_LOG="celery_beat.log"
touch $BEAT_LOG

print_debug "Using celery binary: $CELERY_BIN"
print_debug "Beat log file: $BEAT_LOG"

(
    source "$CONDA_SH" && \
    conda activate keryu && \
    $CELERY_BIN -A keryu3 beat -l INFO > $BEAT_LOG 2>&1
) &
BEAT_PID=$!

# Wait for beat to start and verify it's running
print_status "Waiting for beat to start..."
sleep 5

if ! ps -p $BEAT_PID > /dev/null; then
    print_error "Celery beat scheduler failed to start"
    print_debug "Beat log contents:"
    cat $BEAT_LOG
    exit 1
fi

print_status "Celery beat scheduler is running"

# Start Django development server
print_status "Starting Django development server..."
# Kill any existing Django servers first
pkill -f "manage.py runserver"
sleep 2

# Start the Django server
(source "$CONDA_SH" && conda activate keryu && $PYTHON_BIN manage.py runserver > django.log 2>&1) &
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
verify_single_instance "$CELERY_BIN -A keryu3 worker.*--hostname=$WORKER_NAME"
verify_single_instance "$CELERY_BIN -A keryu3 beat"
verify_single_instance "manage.py runserver" 2  # Allow 2 processes for Django

print_status "All services are running with expected number of instances"
print_status "System is ready for testing"

# Update cleanup to include log files
trap "pkill -f 'celery worker' && pkill -f 'celery beat' && pkill -f 'runserver' && rm -f django.log celery_worker.log celery_beat.log" EXIT
wait $DJANGO_PID 