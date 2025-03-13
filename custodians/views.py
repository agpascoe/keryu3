from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from django.db import transaction
from .forms import (
    CustodianRegistrationForm, CustodianUpdateForm, 
    CustodianProfileForm, SubjectForm
)
from subjects.models import Subject
import logging
import qrcode
from io import BytesIO
from django.core.files import File
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse

logger = logging.getLogger(__name__)

def register(request):
    if request.method == 'POST':
        form = CustodianRegistrationForm(request.POST)
        logger.debug(f"Form data: {request.POST}")
        if form.is_valid():
            logger.debug("Form is valid, creating user")
            try:
                with transaction.atomic():
                    user = form.save()
                    login(request, user)
                    messages.success(request, 'Registration successful! Welcome to Keryu3.')
                    logger.debug("User created successfully, redirecting to dashboard")
                    return redirect('custodians:custodian_dashboard')
            except Exception as e:
                logger.error(f"Error creating user: {str(e)}")
                messages.error(request, 'An error occurred during registration. Please try again.')
                # Add more specific error messages
                if 'phone_number' in str(e):
                    messages.error(request, 'This phone number is already registered.')
                if 'username' in str(e):
                    messages.error(request, 'This username is already taken.')
                if 'email' in str(e):
                    messages.error(request, 'This email is already registered.')
        else:
            logger.debug(f"Form errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustodianRegistrationForm()
    return render(request, 'custodians/register.html', {'form': form})

@login_required
def dashboard(request):
    subjects = Subject.objects.filter(custodian=request.user.custodian)
    return render(request, 'custodians/dashboard.html', {'subjects': subjects})

@login_required
def subject_list(request):
    subject_list = Subject.objects.filter(custodian=request.user.custodian)
    return render(request, 'custodians/subject_list.html', {'subject_list': subject_list})

@login_required
def subject_create(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST, request.FILES)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.custodian = request.user.custodian
            subject.save()
            messages.success(request, 'Subject added successfully!')
            return redirect('custodians:subject_list')
    else:
        form = SubjectForm()
    return render(request, 'custodians/subject_form.html', {
        'form': form,
        'title': 'Add New Subject'
    })

@login_required
def subject_update(request, pk):
    subject = get_object_or_404(Subject, pk=pk, custodian=request.user.custodian)
    if request.method == 'POST':
        form = SubjectForm(request.POST, request.FILES, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject updated successfully!')
            return redirect('custodians:subject_list')
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'custodians/subject_form.html', {
        'form': form,
        'title': 'Update Subject',
        'subject': subject
    })

@login_required
def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk, custodian=request.user.custodian)
    if request.method == 'POST':
        subject.delete()
        messages.success(request, 'Subject deleted successfully!')
        return redirect('custodians:subject_list')
    return render(request, 'custodians/subject_confirm_delete.html', {'subject': subject})

@login_required
def subject_detail(request, pk):
    subject = get_object_or_404(Subject, pk=pk, custodian=request.user.custodian)
    return render(request, 'custodians/subject_detail.html', {'subject': subject})

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = CustodianUpdateForm(request.POST, instance=request.user)
        profile_form = CustodianProfileForm(request.POST, instance=request.user.custodian)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('custodians:custodian_profile')
    else:
        user_form = CustodianUpdateForm(instance=request.user)
        profile_form = CustodianProfileForm(instance=request.user.custodian)
    
    return render(request, 'custodians/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })
