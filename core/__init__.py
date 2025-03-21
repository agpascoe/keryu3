default_app_config = 'core.apps.CoreConfig'

def get_celery_app():
    from .celery import app
    return app

celery_app = None

def get_app():
    global celery_app
    if celery_app is None:
        celery_app = get_celery_app()
    return celery_app

# Only expose get_app to avoid early imports
__all__ = ('get_app',)
