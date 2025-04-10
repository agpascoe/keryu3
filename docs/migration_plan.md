# Alarm System Migration Plan

## Overview
This document outlines the step-by-step plan for safely migrating the alarm system database changes. The migration includes:
1. Standardizing related names
2. Adding database indexes
3. Adding resolution fields
4. Creating NotificationAttempt model

## Pre-Migration Steps

### 1. Backup Strategy
```bash
# Create database backup
pg_dump -U postgres keryu > keryu_backup_$(date +%Y%m%d).sql

# Create backup of media files if any
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/
```

### 2. Development Environment Testing
1. Apply migrations in development
2. Run all tests
3. Verify data integrity
4. Test all affected features

### 3. Rollback Plan
```bash
# Rollback database
psql -U postgres keryu < keryu_backup_$(date +%Y%m%d).sql

# Rollback media files if needed
tar -xzf media_backup_$(date +%Y%m%d).tar.gz
```

## Migration Sequence

### 1. Phase 1: Standardize Related Names
```bash
# Apply migration 0004
python manage.py migrate alarms 0004_standardize_related_names_and_add_indexes
```

Verification steps:
- Check related names in database
- Verify existing relationships
- Test queries using new related names

### 2. Phase 2: Add Resolution Fields and NotificationAttempt
```bash
# Apply migration 0005
python manage.py migrate alarms 0005_add_resolution_fields_and_notification_attempt
```

Verification steps:
- Check new fields in database
- Verify field constraints
- Test new model relationships

## Post-Migration Steps

### 1. Data Verification
```python
# Run verification script
from alarms.models import Alarm, NotificationAttempt
from django.db.models import Count

# Check alarm counts
alarm_count = Alarm.objects.count()
print(f"Total alarms: {alarm_count}")

# Check notification attempts
attempt_count = NotificationAttempt.objects.count()
print(f"Total notification attempts: {attempt_count}")

# Verify indexes
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT indexname, indexdef 
        FROM pg_indexes 
        WHERE tablename = 'alarms_alarm'
    """)
    indexes = cursor.fetchall()
    print("Alarm indexes:", indexes)
```

### 2. Performance Testing
```python
# Test query performance
from django.db import connection
from django.db.models import Q

# Test timestamp index
with connection.cursor() as cursor:
    cursor.execute("EXPLAIN ANALYZE SELECT * FROM alarms_alarm ORDER BY timestamp DESC LIMIT 100")
    print("Timestamp query plan:", cursor.fetchall())

# Test status index
with connection.cursor() as cursor:
    cursor.execute("EXPLAIN ANALYZE SELECT * FROM alarms_alarm WHERE notification_status = 'PENDING'")
    print("Status query plan:", cursor.fetchall())
```

### 3. Application Testing
1. Test alarm creation
2. Test notification sending
3. Test resolution workflow
4. Test notification attempts
5. Verify all API endpoints

## Monitoring Plan

### 1. Database Monitoring
- Monitor query performance
- Watch for any index usage issues
- Track table sizes

### 2. Application Monitoring
- Monitor error rates
- Track notification success rates
- Watch for any performance degradation

## Rollback Triggers
1. Data corruption detected
2. Performance degradation
3. Application errors
4. Failed verification steps

## Timeline
1. Pre-migration: 1 day
2. Migration execution: 1 hour
3. Post-migration verification: 2 hours
4. Monitoring period: 24 hours

## Success Criteria
1. All migrations applied successfully
2. No data loss or corruption
3. All tests passing
4. Performance metrics maintained or improved
5. No application errors
6. All features working as expected

## Communication Plan
1. Notify team of migration schedule
2. Post-migration status update
3. Monitor support channels for issues
4. Document any issues and resolutions

## Next Steps
1. Review and approve migration plan
2. Schedule migration window
3. Execute pre-migration steps
4. Run migration
5. Perform post-migration verification
6. Monitor for issues
7. Document results 