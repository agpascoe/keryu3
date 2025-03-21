from celery import shared_task
from django.conf import settings
import requests
import logging
from django.utils import timezone
from core.celery import app

logger = logging.getLogger(__name__)

@app.task
def create_test_alarm(qr_uuid, location=None):
    """
    Celery task to create an alarm record. Notification will be handled by the signal.
    """
    from subjects.models import SubjectQR  # Import inside function to avoid circular import
    from alarms.models import Alarm  # Import Alarm from alarms.models
    
    try:
        # Get the QR code
        qr = SubjectQR.objects.get(uuid=qr_uuid)
        
        # Create alarm with PENDING status
        alarm = Alarm.objects.create(
            subject=qr.subject,
            qr_code=qr,
            location=location,
            notification_status='PENDING',
            notification_attempts=0,
            is_test=True,  # Mark as test alarm
            timestamp=timezone.now()
        )
        
        logger.info(f"Created test alarm {alarm.id} for subject {qr.subject.name} with PENDING status")
        return alarm.id
        
    except SubjectQR.DoesNotExist:
        logger.error(f"QR code with UUID {qr_uuid} not found")
        raise
    except Exception as e:
        logger.error(f"Error creating test alarm: {str(e)}")
        raise 