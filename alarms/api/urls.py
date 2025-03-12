from django.urls import path
from . import views

app_name = 'alarms_api'

urlpatterns = [
    # These API paths will be implemented later
    path('', views.alarm_list_api, name='alarm_list_api'),
    path('<int:pk>/', views.alarm_detail_api, name='alarm_detail_api'),
] 