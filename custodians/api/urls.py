from django.urls import path
from . import views

app_name = 'custodians_api'

urlpatterns = [
    # These API paths will be implemented later
    path('', views.custodian_list_api, name='custodian_list_api'),
    path('<int:pk>/', views.custodian_detail_api, name='custodian_detail_api'),
] 