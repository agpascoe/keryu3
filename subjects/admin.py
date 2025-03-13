from django.contrib import admin
from .models import Subject, SubjectQR, Alarm

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'custodian', 'date_of_birth', 'gender', 'is_active')
    list_filter = ('gender', 'is_active', 'custodian')
    search_fields = ('name', 'custodian__user__username', 'custodian__user__email')
    date_hierarchy = 'created_at'

@admin.register(SubjectQR)
class SubjectQRAdmin(admin.ModelAdmin):
    list_display = ('subject', 'created_at', 'is_active', 'last_used')
    list_filter = ('is_active', 'subject__custodian')
    search_fields = ('subject__name', 'subject__custodian__user__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('uuid', 'created_at', 'activated_at', 'last_used')

@admin.register(Alarm)
class AlarmAdmin(admin.ModelAdmin):
    list_display = ('subject', 'timestamp', 'location', 'notification_sent')
    list_filter = ('notification_sent', 'subject__custodian')
    search_fields = ('subject__name', 'subject__custodian__user__username', 'location')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp', 'notification_sent', 'notification_error')
