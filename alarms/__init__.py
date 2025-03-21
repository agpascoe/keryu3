default_app_config = 'alarms.apps.AlarmsConfig'

def get_tasks():
    from alarms.tasks import retry_failed_notifications, cleanup_old_alarms
    return retry_failed_notifications, cleanup_old_alarms

__all__ = ['get_tasks']
