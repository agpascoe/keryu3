from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AlarmViewSet,
    NotificationAttemptViewSet,
    alarm_statistics_api,
    retry_notification_api,
)

app_name = 'alarms_api'

router = DefaultRouter(trailing_slash=False)
router.register(r'alarms', AlarmViewSet, basename='alarm')
router.register(r'notification-attempts', NotificationAttemptViewSet, basename='notification-attempt')

urlpatterns = [
    path('', include(router.urls)),
    path('alarms/statistics', alarm_statistics_api, name='alarm-statistics'),
    path('retry-notification/<int:alarm_id>', retry_notification_api, name='retry-notification'),
] 