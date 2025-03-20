from django.urls import path
from . import views

app_name = 'custodians'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('verify-email/<str:uidb64>/<str:token>/', views.verify_email, name='verify_email'),
    path('dashboard/', views.dashboard, name='custodian_dashboard'),
    path('profile/', views.profile, name='custodian_profile'),
    
    # Subject management URLs
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/add/', views.subject_create, name='subject_create'),
    path('subjects/<int:pk>/', views.subject_detail, name='subject_detail'),
    path('subjects/<int:pk>/edit/', views.subject_update, name='subject_update'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),
] 