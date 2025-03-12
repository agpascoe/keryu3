from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Custodian

class CustodianRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)
    phone_number = forms.CharField(max_length=20, required=True, 
                                 help_text='WhatsApp number with country code (e.g., +1234567890)')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 
                 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Update custodian profile
            user.custodian.phone_number = self.cleaned_data['phone_number']
            user.custodian.save()
        return user

class CustodianUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

class CustodianProfileForm(forms.ModelForm):
    class Meta:
        model = Custodian
        fields = ('phone_number', 'emergency_phone', 'address')
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        } 