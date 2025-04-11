from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'alarms'

router = DefaultRouter()
router.register(r'alarms', views.AlarmViewSet, basename='alarm')
router.register(r'notification-attempts', views.NotificationAttemptViewSet, basename='notification_attempt')

urlpatterns = [
    # Include router URLs at the root
    path('', include(router.urls)),
    
    # Traditional view URLs
    path('list/', views.alarm_list, name='alarm_list'),
    path('create/', views.alarm_create, name='alarm_create'),
    path('<int:pk>/', views.alarm_detail, name='alarm_detail'),
    path('<int:pk>/edit/', views.alarm_edit, name='alarm_edit'),
    path('<int:pk>/delete/', views.alarm_delete, name='alarm_delete'),
    path('notifications/', views.notifications, name='notifications'),
    path('statistics/', views.alarm_statistics, name='alarm_statistics'),
    path('statistics/data/', views.statistics_data, name='statistics_data'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('export/excel/', views.export_alarms_excel, name='export_excel'),
    path('webhook/notification/', views.notification_webhook, name='notification_webhook'),
    path('webhook/twilio/status/', views.twilio_status_callback, name='twilio_status_callback'),
] 