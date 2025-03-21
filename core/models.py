from django.db import models
from django.core.exceptions import ValidationError

class SystemParameter(models.Model):
    """System-wide parameters stored in the database"""
    parameter = models.CharField(max_length=50, unique=True)
    value = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "System Parameter"
        verbose_name_plural = "System Parameters"
        ordering = ['parameter']

    def __str__(self):
        return f"{self.parameter}: {self.value}"

    def clean(self):
        """Validate parameter values based on their type"""
        if self.parameter == 'channel':
            if self.value not in ['1', '2', '3']:
                raise ValidationError({
                    'value': 'Channel must be 1 (Meta WhatsApp), 2 (Twilio WhatsApp), or 3 (Twilio SMS)'
                })

    @classmethod
    def get_param(cls, param_name, default=None):
        """Get parameter value by name"""
        try:
            return cls.objects.get(parameter=param_name).value
        except cls.DoesNotExist:
            return default 