import os
import sys
import pytest
import django
from django.conf import settings

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

@pytest.fixture(scope='session')
def django_db_setup():
    """Configure Django database for testing"""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }

@pytest.fixture
def client():
    """A Django test client instance"""
    from django.test.client import Client
    return Client()

@pytest.fixture
def auth_client(client, django_user_model):
    """A Django test client instance with authenticated user"""
    username = "testuser"
    password = "testpass123"
    user = django_user_model.objects.create_user(username=username, password=password)
    client.login(username=username, password=password)
    return client 