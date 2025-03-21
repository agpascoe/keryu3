# Import tasks
from subjects.tasks import create_test_alarm

__all__ = ['create_test_alarm']

default_app_config = 'subjects.apps.SubjectsConfig'

# Import tasks after app is ready to avoid circular imports
def get_tasks():
    from subjects.tasks import create_test_alarm
    return [create_test_alarm]
