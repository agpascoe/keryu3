from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views import AlarmViewSet, NotificationAttemptViewSet

app_name = 'alarms_api'

router = DefaultRouter()
router.register(r'alarms', AlarmViewSet, basename='alarm')
router.register(r'notification-attempts', NotificationAttemptViewSet, basename='notification-attempt')

urlpatterns = [
    path('', include(router.urls)),
] 