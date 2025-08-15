#!/bin/bash

# Keryu Development Environment Script
# Run this in Cursor to manage your development environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Keryu Development Environment${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

# Function to auto-navigate to correct directory
auto_navigate() {
    local current_dir=$(pwd)
    local target_dir="/home/ubuntu/keryu3"
    
    # If we're not in the keryu3 directory, try to navigate there
    if [[ ! -f "manage.py" ]]; then
        print_warning "manage.py not found in current directory"
        print_info "Current directory: $current_dir"
        print_info "Expected directory: $target_dir"
        
        if [[ -d "$target_dir" ]]; then
            print_status "Auto-navigating to correct directory..."
            cd "$target_dir"
            if [[ -f "manage.py" ]]; then
                print_success "Successfully navigated to $(pwd)"
                return 0
            else
                print_error "manage.py still not found after navigation"
                return 1
            fi
        else
            print_error "Target directory $target_dir does not exist"
            print_info "Please ensure the Keryu project is properly installed"
            return 1
        fi
    fi
    
    return 0
}

# Function to check if conda environment is activated
check_conda() {
    if [[ "$CONDA_DEFAULT_ENV" != "keryu" ]]; then
        print_warning "Conda environment 'keryu' not activated"
        print_status "Activating conda environment..."
        
        # Try to activate conda
        if [[ -f "/home/ubuntu/miniconda3/etc/profile.d/conda.sh" ]]; then
            source /home/ubuntu/miniconda3/etc/profile.d/conda.sh
            conda activate keryu
            print_success "Conda environment activated: $CONDA_DEFAULT_ENV"
        else
            print_error "Conda installation not found at expected location"
            print_info "Please ensure conda is properly installed"
            return 1
        fi
    else
        print_status "Conda environment already activated: $CONDA_DEFAULT_ENV"
    fi
}

# Function to check if we're in the right directory
check_directory() {
    if ! auto_navigate; then
        print_error "Directory navigation failed"
        print_info "Please run this script from the keryu3 project directory"
        print_info "Expected location: /home/ubuntu/keryu3"
        exit 1
    fi
    print_status "Working directory: $(pwd)"
}

# Function to validate environment setup
validate_environment() {
    print_status "Validating development environment..."
    
    # Check Django installation
    if ! python -c "import django; print('Django version:', django.get_version())" 2>/dev/null; then
        print_error "Django not found. Please install Django first"
        return 1
    fi
    
    # Check settings file
    if ! python -c "from django.conf import settings; print('Settings loaded successfully')" 2>/dev/null; then
        print_error "Django settings not properly configured"
        return 1
    fi
    
    # Check database
    if ! python manage.py check --database default 2>/dev/null; then
        print_warning "Database connection issues detected"
    fi
    
    print_success "Environment validation completed"
    return 0
}

# Function to check if server is running
check_server() {
    if pgrep -f "python manage.py runserver" > /dev/null; then
        print_status "Development server is running"
        return 0
    else
        print_warning "Development server is not running"
        return 1
    fi
}

# Function to start the server
start_server() {
    print_status "Starting development server..."
    
    # Check if port 8000 is already in use
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_warning "Port 8000 is already in use"
        print_info "Attempting to stop existing server..."
        stop_server
        sleep 2
    fi
    
    DJANGO_SETTINGS_MODULE=core.settings_dev python manage.py runserver 0.0.0.0:8000 &
    local server_pid=$!
    
    # Wait a bit and check if server started successfully
    sleep 3
    if check_server; then
        print_success "Server started successfully!"
        print_status "Access your application at: http://localhost:8000/"
        print_status "Development dashboard at: http://localhost:8000/dev/"
        print_info "Server PID: $server_pid"
    else
        print_error "Failed to start server"
        print_info "Check logs for more details: tail -f django.log"
        exit 1
    fi
}

# Function to stop the server
stop_server() {
    print_status "Stopping development server..."
    local pids=$(pgrep -f "python manage.py runserver")
    
    if [[ -n "$pids" ]]; then
        echo "$pids" | xargs kill -TERM
        sleep 2
        
        # Force kill if still running
        local remaining_pids=$(pgrep -f "python manage.py runserver")
        if [[ -n "$remaining_pids" ]]; then
            print_warning "Force stopping remaining processes..."
            echo "$remaining_pids" | xargs kill -KILL
        fi
        
        print_success "Server stopped successfully!"
    else
        print_info "No server processes found"
    fi
}

# Function to restart the server
restart_server() {
    print_status "Restarting development server..."
    stop_server
    sleep 2
    start_server
}

# Function to show status
show_status() {
    print_header
    check_conda
    check_directory
    validate_environment
    
    echo ""
    print_status "Environment Status:"
    echo "  - Conda Environment: $CONDA_DEFAULT_ENV"
    echo "  - Working Directory: $(pwd)"
    echo "  - Django Settings: core.settings_dev"
    
    if check_server; then
        echo "  - Server Status: ${GREEN}RUNNING${NC}"
        echo "  - Server URL: http://localhost:8000/"
        echo "  - Dev Dashboard: http://localhost:8000/dev/"
        
        # Test server response
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ | grep -q "200"; then
            echo "  - Server Response: ${GREEN}OK${NC}"
        else
            echo "  - Server Response: ${RED}ERROR${NC}"
        fi
    else
        echo "  - Server Status: ${RED}STOPPED${NC}"
    fi
    
    echo ""
    print_status "Quick Commands:"
    echo "  - Start server: $0 start"
    echo "  - Stop server: $0 stop"
    echo "  - Restart server: $0 restart"
    echo "  - Run tests: $0 test"
    echo "  - Create test data: $0 data"
    echo "  - Check Django: python manage.py check"
    echo "  - View logs: tail -f django.log"
    echo "  - Development dashboard: http://localhost:8000/dev/"
}

# Function to run tests
run_tests() {
    print_status "Running development tests..."
    if [[ -f "dev_test.py" ]]; then
        python dev_test.py test
    else
        print_warning "dev_test.py not found, running Django tests..."
        python manage.py test
    fi
}

# Function to create test data
create_test_data() {
    print_status "Creating test data..."
    if [[ -f "dev_test.py" ]]; then
        python dev_test.py create-data
    else
        print_warning "dev_test.py not found"
        print_info "You can create test data manually using Django shell"
    fi
}

# Function to show logs
show_logs() {
    print_status "Showing recent logs..."
    if [[ -f "django.log" ]]; then
        tail -n 50 django.log
    else
        print_warning "django.log not found"
    fi
}

# Function to show help
show_help() {
    print_header
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       - Start the development server"
    echo "  stop        - Stop the development server"
    echo "  restart     - Restart the development server"
    echo "  status      - Show current status"
    echo "  test        - Run development tests"
    echo "  data        - Create test data"
    echo "  logs        - Show recent logs"
    echo "  help        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start    - Start the server"
    echo "  $0 status   - Check current status"
    echo "  $0 test     - Run tests"
    echo "  $0 logs     - View recent logs"
    echo ""
    echo "Development URLs:"
    echo "  - Main App: http://localhost:8000/"
    echo "  - Dev Dashboard: http://localhost:8000/dev/"
}

# Main script logic
case "${1:-status}" in
    "start")
        check_conda
        check_directory
        validate_environment
        start_server
        ;;
    "stop")
        stop_server
        ;;
    "restart")
        check_conda
        check_directory
        validate_environment
        restart_server
        ;;
    "status")
        show_status
        ;;
    "test")
        check_conda
        check_directory
        run_tests
        ;;
    "data")
        check_conda
        check_directory
        create_test_data
        ;;
    "logs")
        check_directory
        show_logs
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac 