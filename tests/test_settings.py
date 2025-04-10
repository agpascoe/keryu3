from core.settings import *

# Test-specific settings
DEBUG = False

# SSL/HTTPS settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Disable migrations during tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Configure test client
TEST_CLIENT_DEFAULTS = {
    'wsgi.url_scheme': 'https',
    'HTTP_X_FORWARDED_PROTO': 'https',
    'SERVER_NAME': 'keryu.mx',
    'SERVER_PORT': '443'
}

# Configure REST framework for testing
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '1000/day',  # Increased for tests
        'user': '2000/day',  # Increased for tests
    },
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'APPEND_SLASH': False,
}

# Disable throttling for tests except in rate_limiting test
class DisableThrottlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.endswith('/token/') or 'test_rate_limiting' not in request.META.get('PATH_INFO', ''):
            request.META['DISABLE_THROTTLING'] = True
        return self.get_response(request)

MIDDLEWARE = ['tests.test_settings.DisableThrottlingMiddleware'] + MIDDLEWARE 