from django import template
from django.template.defaultfilters import floatformat

register = template.Library()

@register.filter
def percentage(value, total):
    try:
        return floatformat((float(value) / float(total)) * 100.0, 1)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def subtract(value, arg):
    try:
        return value - arg
    except (ValueError, TypeError):
        return 0 