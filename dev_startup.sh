#!/bin/bash

echo "⚠️  DEPRECATED: dev_startup.sh is deprecated!"
echo "📌 Use: ./startup.sh dev"
echo "💡 Or use enhanced: ./dev_env.sh start"
echo "🔄 Redirecting to startup.sh dev in 3 seconds..."
sleep 3
exec ./startup.sh dev

# Activate conda environment
source /home/ubuntu/miniconda3/etc/profile.d/conda.sh
conda activate keryu

# Change to project directory
cd /home/ubuntu/keryu3

# Function to cleanup on exit
cleanup() {
    echo "Stopping development server..."
    if [ ! -z "$DJANGO_PID" ]; then
        kill $DJANGO_PID 2>/dev/null || true
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if port 8000 is available
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "Port 8000 is already in use. Stopping existing process..."
    lsof -ti:8000 | xargs kill -9
    sleep 2
fi

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
echo "Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(is_superuser=True).exists():
    print('Creating superuser...')
    User.objects.create_superuser('admin', 'admin@keryu.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

# Start Django development server
echo "Starting Django development server..."
echo "Development server will be available at: http://localhost:8000"
echo "Admin interface: http://localhost:8000/admin"
echo "Press Ctrl+C to stop the server"

# Start the server in the background
DJANGO_SETTINGS_MODULE=core.settings_dev python manage.py runserver 0.0.0.0:8000 &
DJANGO_PID=$!

# Wait for the server to start
sleep 3

# Check if server started successfully
if ! kill -0 $DJANGO_PID 2>/dev/null; then
    echo "Failed to start Django development server"
    exit 1
fi

echo "Development server started successfully!"
echo "PID: $DJANGO_PID"

# Keep the script running
wait $DJANGO_PID 