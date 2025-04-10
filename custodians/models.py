from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)

class Custodian(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = PhoneNumberField(help_text='WhatsApp phone number')
    emergency_phone = PhoneNumberField(blank=True, null=True, help_text='Alternative emergency contact')
    address = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=4, null=True, blank=True)
    verification_code_timestamp = models.DateTimeField(null=True, blank=True)
    verification_attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

    def generate_verification_code(self):
        """Generate a new 4-digit verification code and save it"""
        import random
        self.verification_code = ''.join(random.choices('0123456789', k=4))
        self.verification_code_timestamp = timezone.now()
        self.verification_attempts = 0
        self.save(update_fields=['verification_code', 'verification_code_timestamp', 'verification_attempts'])
        return self.verification_code

    def verify_phone_code(self, code):
        """Verify the provided code and mark phone as verified if correct"""
        if not self.verification_code or not self.verification_code_timestamp:
            return False
        
        # Check if code is expired (15 minutes)
        if timezone.now() > self.verification_code_timestamp + timezone.timedelta(minutes=15):
            return False
        
        if code == self.verification_code:
            self.phone_verified = True
            self.verification_code = None
            self.verification_code_timestamp = None
            self.save(update_fields=['phone_verified', 'verification_code', 'verification_code_timestamp'])
            return True
            
        self.verification_attempts += 1
        self.save(update_fields=['verification_attempts'])
        return False

    class Meta:
        ordering = ['-created_at']

@receiver(pre_save, sender=User)
def prepare_user_save(sender, instance, **kwargs):
    """Prepare user for saving by ensuring email is unique"""
    if instance.email:
        # Check if email is unique, excluding current instance
        if User.objects.filter(email=instance.email).exclude(id=instance.id).exists():
            raise ValueError("This email address is already in use.")

@receiver(post_save, sender=User)
def create_custodian(sender, instance, created, **kwargs):
    """Create a Custodian profile whenever a new User is created"""
    if created:
        try:
            # Check if custodian already exists
            try:
                instance.custodian
                logger.debug(f"Custodian already exists for user {instance.id}")
                return
            except ObjectDoesNotExist:
                pass
            
            # Create new custodian within transaction
            with transaction.atomic():
                Custodian.objects.create(user=instance)
                logger.debug(f"Created new custodian for user {instance.id}")
        except Exception as e:
            logger.error(f"Error creating custodian for user {instance.id}: {str(e)}", exc_info=True)
            # Don't raise the error to prevent breaking the admin interface
            # but log it for debugging

@receiver(post_save, sender=User)
def save_custodian(sender, instance, created, **kwargs):
    """Ensure the Custodian profile is saved when User is saved"""
    if not created:  # Only handle updates, not creation
        try:
            # Check if custodian exists before saving
            try:
                custodian = instance.custodian
                if custodian.pk:  # Only save if custodian exists in database
                    custodian.save()
                    logger.debug(f"Updated existing custodian for user {instance.id}")
            except ObjectDoesNotExist:
                # Create custodian if it doesn't exist during update
                with transaction.atomic():
                    Custodian.objects.create(user=instance)
                    logger.debug(f"Created missing custodian for user {instance.id} during update")
        except Exception as e:
            logger.error(f"Error saving custodian for user {instance.id}: {str(e)}", exc_info=True)
            # Don't raise the error to prevent breaking the admin interface
            # but log it for debugging
