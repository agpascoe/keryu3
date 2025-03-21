from django.contrib import admin
from .models import Subject, SubjectQR

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'custodian', 'date_of_birth', 'gender', 'is_active')
    list_filter = ('is_active', 'gender')
    search_fields = ('name', 'custodian__user__username', 'medical_conditions')
    date_hierarchy = 'created_at'

@admin.register(SubjectQR)
class SubjectQRAdmin(admin.ModelAdmin):
    list_display = ('subject', 'uuid', 'is_active', 'created_at', 'last_used')
    list_filter = ('is_active',)
    search_fields = ('subject__name', 'uuid')
    date_hierarchy = 'created_at'
