from django import forms
from .models import Subject
from phonenumber_field.formfields import PhoneNumberField

class SubjectForm(forms.ModelForm):
    doctor_phone = PhoneNumberField(required=False, help_text='Enter phone number in international format')

    class Meta:
        model = Subject
        fields = [
            'name', 'date_of_birth', 'gender', 'custodian',
            'medical_conditions', 'allergies', 'medications',
            'doctor_name', 'doctor_phone', 'doctor_address',
            'doctor_speciality', 'photo', 'is_active'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'medical_conditions': forms.Textarea(attrs={'rows': 3}),
            'allergies': forms.Textarea(attrs={'rows': 3}),
            'medications': forms.Textarea(attrs={'rows': 3}),
            'doctor_address': forms.Textarea(attrs={'rows': 3}),
        } 