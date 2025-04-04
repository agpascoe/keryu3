#!/bin/bash

echo "Starting Keryu services shutdown sequence..."

# Kill any running Django development server
echo "Stopping Django development server..."
if pgrep -f "runserver"; then
    pkill -9 -f "runserver"
    echo "✓ Django development server killed"
else
    echo "No Django development server running"
fi

# Stop Nginx
echo "Stopping Nginx..."
sudo systemctl stop nginx
echo "✓ Nginx stopped"

# Stop Redis
echo "Stopping Redis..."
sudo systemctl stop redis
echo "✓ Redis stopped"

# Kill any remaining Gunicorn processes
echo "Stopping any Gunicorn processes..."
if pgrep -f "gunicorn"; then
    sudo pkill -9 -f "gunicorn"
    echo "✓ Gunicorn processes killed"
else
    echo "No Gunicorn processes running"
fi

# Kill any remaining Celery processes - with multiple attempts
echo "Stopping any Celery processes..."
for attempt in {1..3}; do
    if pgrep -f "celery"; then
        sudo pkill -9 -f "celery"
        echo "Attempt $attempt: Killed Celery processes"
        sleep 2
    else
        echo "No Celery processes running"
        break
    fi
done

# Force kill any remaining Celery processes
if pgrep -f "celery"; then
    echo "Force killing remaining Celery processes..."
    # Find all celery PIDs and kill each one directly
    for pid in $(pgrep -f "celery"); do
        sudo kill -9 $pid 2>/dev/null || true
    done
fi

echo -e "\nVerifying all processes are stopped:"

# Final verification - more thorough
if pgrep -f "runserver|gunicorn|celery" > /dev/null; then
    echo "! Warning: Some processes are still running"
    pgrep -af "runserver|gunicorn|celery"
    echo -e "\nTrying one final force kill..."
    sudo pkill -9 -f "celery|gunicorn|runserver" || true
    sleep 2
    if pgrep -f "runserver|gunicorn|celery" > /dev/null; then
        echo "! Some processes could not be killed"
        exit 1
    else
        echo "✓ All processes stopped after final attempt"
    fi
else
    echo "✓ All processes stopped"
fi

# Verify services
for service in nginx redis; do
    if systemctl is-active --quiet $service; then
        echo "! Warning: $service is still running"
        sudo systemctl stop $service
        echo "Stopped $service"
    else
        echo "✓ $service is stopped"
    fi
done

echo -e "\n✓ All services and processes successfully stopped" 