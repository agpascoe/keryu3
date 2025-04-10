from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber
from .models import Custodian
from subjects.models import Subject
from django.db import transaction
import re
import logging

logger = logging.getLogger(__name__)

class CustodianRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        help_text='Mexican phone number (10 digits, +52 will be added if not provided)',
        error_messages={
            'invalid': 'Enter a valid Mexican phone number (e.g., 1234567890 or +521234567890)',
        }
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email

    def clean_phone_number(self):
        """Clean and format Mexican phone numbers"""
        try:
            phone = self.cleaned_data['phone_number']
            logger.debug(f"Cleaning phone number: {phone}")
            
            # Remove any spaces, dashes, or other characters
            phone_digits = ''.join(filter(str.isdigit, phone))
            logger.debug(f"Phone digits after cleaning: {phone_digits}")
            
            # Handle different cases
            formatted_number = None
            if len(phone_digits) == 10:
                # Add +52 prefix for 10-digit Mexican numbers
                formatted_number = f'+52{phone_digits}'
            elif len(phone_digits) == 12 and phone_digits.startswith('52'):
                # Already has country code
                formatted_number = f'+{phone_digits}'
            elif len(phone_digits) == 13 and phone_digits.startswith('521'):
                # Has country code with extra 1
                formatted_number = f'+{phone_digits}'
                
            if formatted_number:
                logger.debug(f"Formatted number: {formatted_number}")
                # Create a PhoneNumber instance for validation only
                phone_number = PhoneNumber.from_string(formatted_number, region='MX')
                if phone_number and phone_number.is_valid():
                    # Return the string representation
                    return str(phone_number)
                    
            raise forms.ValidationError('Please enter a valid 10-digit Mexican phone number')
            
        except Exception as e:
            logger.error(f"Error formatting phone number: {str(e)}")
            raise forms.ValidationError('Please enter a valid 10-digit Mexican phone number')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']
        
        if commit:
            user.save()
            # Update custodian profile
            user.custodian.phone_number = self.cleaned_data['phone_number']
            user.custodian.save()
        
        return user

class SubjectForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text='Select the date of birth'
    )
    
    class Meta:
        model = Subject
        fields = [
            'name', 'date_of_birth', 'gender', 'medical_conditions',
            'allergies', 'medications', 'doctor_name', 'doctor_phone',
            'doctor_address', 'doctor_speciality', 'photo'
        ]
        widgets = {
            'medical_conditions': forms.Textarea(attrs={'rows': 3}),
            'allergies': forms.Textarea(attrs={'rows': 3}),
            'medications': forms.Textarea(attrs={'rows': 3}),
            'doctor_address': forms.Textarea(attrs={'rows': 2}),
        }

class CustodianUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class CustodianProfileForm(forms.ModelForm):
    phone_number = PhoneNumberField(
        required=True,
        help_text='WhatsApp number with country code (e.g., +1234567890)',
        error_messages={
            'invalid': 'Enter a valid phone number (e.g., +1234567890)',
        },
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1234567890'
        })
    )
    emergency_phone = PhoneNumberField(
        required=False,
        help_text='Alternative emergency contact number (optional)',
        error_messages={
            'invalid': 'Enter a valid phone number (e.g., +1234567890)',
        },
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1234567890'
        })
    )

    class Meta:
        model = Custodian
        fields = ('phone_number', 'emergency_phone', 'address')
        widgets = {
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter your address'
            }),
        } 