from django.urls import path
from . import views

app_name = 'alarms_api'

urlpatterns = [
    # These API paths will be implemented later
    path('', views.alarm_list_api, name='alarm_list_api'),
    path('<int:pk>/', views.alarm_detail_api, name='alarm_detail_api'),
    path('statistics/', views.alarm_statistics_api, name='alarm_statistics_api'),
    path('<int:alarm_id>/retry-notification/', views.retry_notification_api, name='retry_notification_api'),
] 