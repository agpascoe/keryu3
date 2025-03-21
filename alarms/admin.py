from django.contrib import admin
from .models import Alarm

@admin.register(Alarm)
class AlarmAdmin(admin.ModelAdmin):
    list_display = ('subject', 'timestamp', 'location', 'notification_sent', 'notification_status')
    list_filter = ('notification_sent', 'notification_status', 'subject__custodian')
    search_fields = ('subject__name', 'subject__custodian__user__username', 'location')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp', 'created_at', 'updated_at')
