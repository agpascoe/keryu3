#!/bin/bash

# Enable color output
tput init

# Colors
GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 3)
NC=$(tput sgr0)

# Function for consistent status messages
print_message() {
    local status="$1"
    local message="$2"
    local result="$3"
    printf "%-6s %-30s %s\n" "" "$message" "$result"
}

print_result() {
    local type="$1"
    local message="$2"
    local symbol=""
    local color=""
    
    case "$type" in
        "success")
            symbol="✓"
            color="$GREEN"
            ;;
        "info")
            symbol="•"
            color="$YELLOW"
            ;;
        *)
            symbol="!"
            color="$YELLOW"
            ;;
    esac
    
    echo -en "${color}[${symbol}]${NC} ${message}"
}

print_header() {
    echo
    echo "=== $1 ==="
    echo
}

print_header "Starting Keryu Services Shutdown Sequence"

# Kill any running Django development server
if pgrep -f "runserver" > /dev/null; then
    pkill -9 -f "runserver" 2>/dev/null
    print_message "" "Django development server" "$(print_result success 'Killed')"
else
    print_message "" "Django development server" "$(print_result info 'Not running')"
fi

# Stop Nginx
sudo systemctl stop nginx 2>/dev/null
print_message "" "Nginx" "$(print_result success 'Stopped')"

# Stop Redis
sudo systemctl stop redis 2>/dev/null
print_message "" "Redis" "$(print_result success 'Stopped')"

# Kill any remaining Gunicorn processes
if pgrep -f "gunicorn" > /dev/null; then
    sudo pkill -9 -f "gunicorn" 2>/dev/null
    print_message "" "Gunicorn processes" "$(print_result success 'Killed')"
else
    print_message "" "Gunicorn processes" "$(print_result info 'Not running')"
fi

# Kill any remaining Celery processes
celery_stopped=false
for attempt in {1..3}; do
    if pgrep -f "celery" > /dev/null; then
        sudo pkill -9 -f "celery" 2>/dev/null
        sleep 1
    else
        celery_stopped=true
        break
    fi
done

if [ "$celery_stopped" = true ]; then
    print_message "" "Celery processes" "$(print_result success 'Stopped')"
else
    print_message "" "Celery processes" "$(print_result warning 'Force killing...')"
    for pid in $(pgrep -f "celery"); do
        sudo kill -9 $pid 2>/dev/null || true
    done
fi

print_header "Verifying Processes"

if pgrep -f "runserver|gunicorn|celery" > /dev/null; then
    print_message "" "Process check" "$(print_result warning 'Some processes still running')"
    pgrep -af "runserver|gunicorn|celery"
    echo
    print_message "" "Final force kill" "$(print_result warning 'Attempting...')"
    sudo pkill -9 -f "celery|gunicorn|runserver" 2>/dev/null || true
    sleep 1
    if pgrep -f "runserver|gunicorn|celery" > /dev/null; then
        print_message "" "Force kill result" "$(print_result warning 'Failed to stop all processes')"
        exit 1
    else
        print_message "" "Force kill result" "$(print_result success 'All processes stopped')"
    fi
else
    print_message "" "Process check" "$(print_result success 'All processes stopped')"
fi

print_header "Final Service Status Check"

for service in nginx redis; do
    if systemctl is-active --quiet $service; then
        print_message "" "$service status" "$(print_result warning 'Still running')"
        sudo systemctl stop $service 2>/dev/null
        print_message "" "$service" "$(print_result success 'Stopped')"
    else
        print_message "" "$service status" "$(print_result success 'Stopped')"
    fi
done

print_header "Shutdown Sequence Complete"
print_message "" "Final status" "$(print_result success 'All services and processes stopped')"
echo 