from django.urls import path
from . import views

app_name = 'subjects'

urlpatterns = [
    # User views
    path('', views.user_subject_list, name='list'),  # Regular user view
    path('create/', views.subject_create, name='create'),  # Regular user subject creation
    path('<int:pk>/', views.subject_detail, name='detail'),  # Regular user subject detail
    path('<int:pk>/edit/', views.subject_edit, name='edit'),  # Regular user subject edit
    path('<int:pk>/delete/', views.subject_delete, name='delete'),  # Regular user subject delete
    path('stats/', views.subject_stats, name='stats'),
    path('qr/', views.qr_codes, name='qr_codes'),
    
    # QR code related views
    path('qr/generate/', views.generate_qr, name='generate_qr'),
    path('qr/assign/', views.assign_qr, name='assign_qr'),  # Default assign endpoint
    path('qr/<uuid:uuid>/assign/', views.assign_qr, name='assign_qr_with_uuid'),  # Assign with UUID
    path('qr/<uuid:uuid>/image/', views.qr_image, name='qr_image'),
    path('qr/<uuid:uuid>/download/', views.download_qr, name='download_qr'),
    path('qr/<uuid:uuid>/activate/', views.activate_qr, name='activate_qr'),
    path('qr/<uuid:uuid>/deactivate/', views.deactivate_qr, name='deactivate_qr'),
    path('qr/<uuid:uuid>/delete/', views.delete_qr, name='delete_qr'),
    path('qr/print/', views.print_qr, name='print_qr'),  # Default print endpoint
    path('qr/<uuid:uuid>/scan/', views.scan_qr, name='scan_qr'),
    path('qr/<uuid:uuid>/scan/anonymous/', views.scan_qr_anonymous, name='scan_qr_anonymous'),  # Anonymous scan route
    path('qr/<uuid:uuid>/trigger/', views.trigger_qr, name='trigger_qr'),
    path('qr/<uuid:uuid>/toggle/', views.toggle_qr_status, name='toggle_qr_status'),
    
    # Admin views (prefixed with admin/)
    path('admin/subjects/', views.subject_list, name='subject_list'),
    path('admin/subjects/stats/', views.subject_stats, name='subject_stats'),
    path('admin/qr/regenerate-all/', views.regenerate_all_qr_images, name='regenerate_all_qr_images'),
] 