from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from phonenumber_field.formfields import PhoneNumberField
from .models import Custodian
from subjects.models import Subject
from django.db import transaction

class CustodianRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)
    phone_number = PhoneNumberField(
        required=True,
        help_text='WhatsApp number with country code (e.g., +1234567890)',
        error_messages={
            'invalid': 'Enter a valid phone number (e.g., +1234567890)',
        }
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 
                 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        # Use full email as username
        user.username = self.cleaned_data['email']
        
        if commit:
            user.save()
        else:
            user.save()  # We need to save the user to create the custodian profile
            
        # Always update custodian profile
        custodian = user.custodian
        custodian.phone_number = self.cleaned_data['phone_number']
        custodian.save()
        
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