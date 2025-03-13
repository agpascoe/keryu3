from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Custodian

class CustodianInline(admin.StackedInline):
    model = Custodian
    can_delete = False
    verbose_name_plural = 'Custodian Profile'

class CustomUserAdmin(UserAdmin):
    inlines = (CustodianInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_phone_number')
    
    def get_phone_number(self, obj):
        return obj.custodian.phone_number if hasattr(obj, 'custodian') else '-'
    get_phone_number.short_description = 'Phone Number'

# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
