from django.urls import path
from . import views

app_name = 'alarms'

urlpatterns = [
    # These paths will be implemented later
    path('', views.alarm_list, name='alarm_list'),
    path('create/', views.alarm_create, name='alarm_create'),
    path('<int:pk>/', views.alarm_detail, name='alarm_detail'),
    path('<int:pk>/edit/', views.alarm_edit, name='alarm_edit'),
    path('<int:pk>/delete/', views.alarm_delete, name='alarm_delete'),
    path('notifications/', views.notifications, name='notifications'),
    path('statistics/', views.alarm_statistics, name='alarm_statistics'),
    path('statistics/data/', views.statistics_data, name='statistics_data'),
    path('dashboard/', views.admin_alarm_dashboard, name='admin_dashboard'),
    path('<int:alarm_id>/retry-notification/', views.retry_notification, name='retry_notification'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('export/excel/', views.export_alarms_excel, name='export_excel'),
    path('export/pdf/', views.export_alarms_pdf, name='export_pdf'),
] 