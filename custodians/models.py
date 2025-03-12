from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField

class Custodian(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = PhoneNumberField(help_text='WhatsApp phone number')
    emergency_phone = PhoneNumberField(blank=True, null=True, help_text='Alternative emergency contact')
    address = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

    class Meta:
        ordering = ['-created_at']

class Subject(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]

    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    medical_conditions = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    medications = models.TextField(blank=True)
    custodian = models.ForeignKey(Custodian, on_delete=models.CASCADE, related_name='subjects')
    doctor_name = models.CharField(max_length=100, blank=True, help_text='Primary care physician')
    doctor_phone = PhoneNumberField(blank=True, null=True, help_text='Doctor\'s contact number')
    doctor_address = models.TextField(blank=True, help_text='Doctor\'s office address')
    doctor_speciality = models.CharField(max_length=100, blank=True, help_text='Doctor\'s speciality')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    photo = models.ImageField(upload_to='subject_photos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} (Custodian: {self.custodian})"

    class Meta:
        ordering = ['name']

@receiver(post_save, sender=User)
def create_custodian(sender, instance, created, **kwargs):
    """Create a Custodian profile whenever a new User is created"""
    if created:
        Custodian.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_custodian(sender, instance, **kwargs):
    """Ensure the Custodian profile is saved when User is saved"""
    instance.custodian.save()
