from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Count
from alarms.models import Alarm, NotificationAttempt
from django.utils import timezone

class Command(BaseCommand):
    help = 'Verifies the results of the alarm system migration'

    def handle(self, *args, **options):
        self.stdout.write('Starting migration verification...')
        
        # 1. Check model counts
        self.stdout.write('\n1. Checking model counts...')
        alarm_count = Alarm.objects.count()
        self.stdout.write(f'Total alarms: {alarm_count}')
        
        attempt_count = NotificationAttempt.objects.count()
        self.stdout.write(f'Total notification attempts: {attempt_count}')
        
        # 2. Verify indexes
        self.stdout.write('\n2. Verifying indexes...')
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT indexname, indexdef 
                FROM pg_indexes 
                WHERE tablename = 'alarms_alarm'
            """)
            indexes = cursor.fetchall()
            self.stdout.write('Alarm indexes:')
            for index in indexes:
                self.stdout.write(f'  - {index[0]}: {index[1]}')
        
        # 3. Check notification status distribution
        self.stdout.write('\n3. Checking notification status distribution...')
        status_counts = Alarm.objects.values('notification_status').annotate(count=Count('id'))
        for status in status_counts:
            self.stdout.write(f'  {status["notification_status"]}: {status["count"]}')
        
        # 4. Verify resolution fields
        self.stdout.write('\n4. Verifying resolution fields...')
        resolved_count = Alarm.objects.filter(resolved_at__isnull=False).count()
        self.stdout.write(f'Resolved alarms: {resolved_count}')
        
        # 5. Check notification attempts
        self.stdout.write('\n5. Checking notification attempts...')
        channel_counts = NotificationAttempt.objects.values('channel').annotate(count=Count('id'))
        for channel in channel_counts:
            self.stdout.write(f'  {channel["channel"]}: {channel["count"]}')
        
        # 6. Performance check
        self.stdout.write('\n6. Running performance checks...')
        with connection.cursor() as cursor:
            # Test timestamp index
            cursor.execute("EXPLAIN ANALYZE SELECT * FROM alarms_alarm ORDER BY timestamp DESC LIMIT 100")
            self.stdout.write('\nTimestamp query plan:')
            for row in cursor.fetchall():
                self.stdout.write(f'  {row[0]}')
            
            # Test status index
            cursor.execute("EXPLAIN ANALYZE SELECT * FROM alarms_alarm WHERE notification_status = 'PENDING'")
            self.stdout.write('\nStatus query plan:')
            for row in cursor.fetchall():
                self.stdout.write(f'  {row[0]}')
        
        # 7. Data integrity checks
        self.stdout.write('\n7. Running data integrity checks...')
        
        # Check for alarms without subjects
        orphaned_alarms = Alarm.objects.filter(subject__isnull=True).count()
        self.stdout.write(f'Alarms without subjects: {orphaned_alarms}')
        
        # Check for notification attempts without alarms
        orphaned_attempts = NotificationAttempt.objects.filter(alarm__isnull=True).count()
        self.stdout.write(f'Notification attempts without alarms: {orphaned_attempts}')
        
        # Check for invalid status transitions
        self.stdout.write('\n8. Checking status transitions...')
        recent_alarms = Alarm.objects.filter(
            created_at__gte=timezone.now() - timezone.timedelta(hours=24)
        )
        for alarm in recent_alarms:
            if alarm.notification_status == 'SENT' and not alarm.notification_sent:
                self.stdout.write(f'Warning: Alarm {alarm.id} has SENT status but notification_sent is False')
        
        self.stdout.write('\nVerification complete!') 