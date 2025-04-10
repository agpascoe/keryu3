from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Custodian
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

class CustodianInline(admin.StackedInline):
    model = Custodian
    can_delete = False
    verbose_name_plural = 'Custodian Profile'
    
    def get_min_num(self, request, obj=None, **kwargs):
        """Ensure at least one custodian profile is created"""
        return 1 if not obj else 0

class CustomUserAdmin(UserAdmin):
    inlines = (CustodianInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_phone_number')
    
    def get_phone_number(self, obj):
        try:
            return obj.custodian.phone_number if hasattr(obj, 'custodian') else '-'
        except ObjectDoesNotExist:
            return '-'
    get_phone_number.short_description = 'Phone Number'
    
    def save_model(self, request, obj, form, change):
        """Override save_model to handle User and Custodian creation in a transaction"""
        try:
            with transaction.atomic():
                # First save the user
                super().save_model(request, obj, form, change)
                
                # If this is a new user and no custodian exists, create one
                if not change:
                    try:
                        obj.custodian
                    except ObjectDoesNotExist:
                        Custodian.objects.create(user=obj)
        except Exception as e:
            # Log the error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error saving user/custodian in admin: {str(e)}")
            raise
    
    def save_formset(self, request, form, formset, change):
        """Override save_formset to handle inline saves properly"""
        if formset.model == Custodian:
            try:
                with transaction.atomic():
                    instances = formset.save(commit=False)
                    
                    # Handle deletion
                    for obj in formset.deleted_objects:
                        obj.delete()
                    
                    # Handle updates/creation
                    for instance in instances:
                        # Ensure we don't have duplicate custodians
                        try:
                            existing = Custodian.objects.get(user=form.instance)
                            if existing != instance:
                                existing.delete()
                        except Custodian.DoesNotExist:
                            pass
                        
                        instance.user = form.instance
                        instance.save()
                    
                    formset.save_m2m()
            except Exception as e:
                # Log the error
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error saving custodian formset in admin: {str(e)}")
                raise
        else:
            formset.save()
    
    def delete_model(self, request, obj):
        """Override delete_model to ensure proper cleanup"""
        try:
            with transaction.atomic():
                # Delete custodian first to avoid foreign key issues
                try:
                    if hasattr(obj, 'custodian'):
                        obj.custodian.delete()
                except ObjectDoesNotExist:
                    pass
                
                super().delete_model(request, obj)
        except Exception as e:
            # Log the error
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error deleting user/custodian in admin: {str(e)}")
            raise

# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
