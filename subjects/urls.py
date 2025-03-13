from django.urls import path
from . import views

app_name = 'subjects'

urlpatterns = [
    # Admin views
    path('admin/subjects/', views.subject_list, name='subject_list'),
    path('admin/subjects/create/', views.subject_create, name='subject_create'),
    path('admin/subjects/<int:pk>/', views.subject_detail, name='subject_detail'),
    path('admin/subjects/<int:pk>/edit/', views.subject_edit, name='subject_edit'),
    path('admin/subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),
    path('admin/subjects/stats/', views.subject_stats, name='subject_stats'),
    path('admin/subjects/qr-codes/', views.qr_codes, name='qr_codes'),
] 