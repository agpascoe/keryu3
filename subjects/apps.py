from django.apps import AppConfig


class SubjectsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'subjects'

    def ready(self):
        import subjects.receivers  # noqa
