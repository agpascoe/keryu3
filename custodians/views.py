from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from django.db import transaction
from .forms import CustodianRegistrationForm, CustodianUpdateForm, CustodianProfileForm

def register(request):
    if request.method == 'POST':
        form = CustodianRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Keryu3.')
            return redirect('custodian_dashboard')
    else:
        form = CustodianRegistrationForm()
    return render(request, 'custodians/register.html', {'form': form})

@login_required
def dashboard(request):
    return render(request, 'custodians/dashboard.html')

@login_required
@transaction.atomic
def profile(request):
    if request.method == 'POST':
        user_form = CustodianUpdateForm(request.POST, instance=request.user)
        profile_form = CustodianProfileForm(request.POST, instance=request.user.custodian)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('custodian_profile')
    else:
        user_form = CustodianUpdateForm(instance=request.user)
        profile_form = CustodianProfileForm(instance=request.user.custodian)
    
    return render(request, 'custodians/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })
