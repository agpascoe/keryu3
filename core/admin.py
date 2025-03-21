from django.contrib import admin
from .models import SystemParameter

@admin.register(SystemParameter)
class SystemParameterAdmin(admin.ModelAdmin):
    list_display = ('parameter', 'value', 'description', 'updated_at')
    list_filter = ('parameter',)
    search_fields = ('parameter', 'value', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_readonly_fields(self, request, obj=None):
        """Make parameter field readonly only on edit"""
        if obj:  # editing an existing object
            return self.readonly_fields + ('parameter',)
        return self.readonly_fields 