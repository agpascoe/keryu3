from django.urls import path
from . import views

app_name = 'custodians'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='custodian_dashboard'),
    path('profile/', views.profile, name='custodian_profile'),
] 