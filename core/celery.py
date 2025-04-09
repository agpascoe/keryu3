import os
from celery import Celery
from celery.schedules import crontab
from kombu import Queue, Exchange

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Create the Celery application
app = Celery('keryu3')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Define queues
app.conf.task_queues = (
    Queue('default', Exchange('default'), routing_key='default'),
    Queue('alarms', Exchange('alarms'), routing_key='alarms'),
    Queue('subjects', Exchange('subjects'), routing_key='subjects'),
)

# Configure task routing
app.conf.task_routes = {
    'alarms.tasks.*': {'queue': 'alarms'},
    'subjects.tasks.*': {'queue': 'subjects'},
}

# Configure periodic tasks
app.conf.beat_schedule = {
    'process-pending-alarms': {
        'task': 'alarms.tasks.process_pending_alarms',
        'schedule': 60.0,  # Run every 60 seconds
    },
    'cleanup-old-alarms': {
        'task': 'alarms.tasks.cleanup_old_alarms',
        'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
    }
}

# Explicitly set Redis as the broker and result backend
app.conf.update(
    broker_url=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    result_backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Prevent duplicate task execution
    task_acks_late=True,  # Acknowledge tasks only after completion
    task_track_started=True,  # Track when tasks are started
    task_default_rate_limit='30/m',  # Limit task execution rate
    worker_prefetch_multiplier=1,  # Process one task at a time
    worker_concurrency=1,  # Run only one worker process
)

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 