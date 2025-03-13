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
    path('qr/generate/', views.generate_qr, name='generate_qr'),
    path('qr/<uuid:uuid>/image/', views.qr_image, name='qr_image'),
    path('qr/<uuid:uuid>/download/', views.download_qr, name='download_qr'),
    path('qr/<uuid:uuid>/activate/', views.activate_qr, name='activate_qr'),
    path('qr/<uuid:uuid>/deactivate/', views.deactivate_qr, name='deactivate_qr'),
    path('qr/<uuid:uuid>/delete/', views.delete_qr, name='delete_qr'),
    path('qr/<uuid:uuid>/scan/', views.scan_qr, name='scan_qr'),
] 