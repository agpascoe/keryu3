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
] 