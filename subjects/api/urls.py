from django.urls import path
from . import views

app_name = 'subjects_api'

urlpatterns = [
    # These API paths will be implemented later
    path('', views.subject_list_api, name='subject_list_api'),
    path('<int:pk>/', views.subject_detail_api, name='subject_detail_api'),
] 