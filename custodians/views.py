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
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMultiAlternatives
from .tokens import email_verification_token
from django.contrib.auth.models import User
from core.email_backend import PopupEmailBackend
import re
from custodians.models import Custodian
from alarms.models import Alarm

logger = logging.getLogger(__name__)

def register(request):
    if request.method == 'POST':
        form = CustodianRegistrationForm(request.POST)
        logger.debug(f"Form data: {request.POST}")
        if form.is_valid():
            logger.debug("Form is valid, creating user")
            try:
                with transaction.atomic():
                    # Create user but don't activate yet
                    user = form.save(commit=False)
                    user.is_active = False
                    user.save()
                    
                    # Generate verification token
                    current_site = get_current_site(request)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = email_verification_token.make_token(user)
                    verification_url = request.build_absolute_uri(
                        reverse('custodians:verify_email', kwargs={'uidb64': uid, 'token': token})
                    )
                    
                    # Context for email templates
                    context = {
                        'user': user,
                        'domain': current_site.domain,
                        'uid': uid,
                        'token': token,
                    }
                    
                    # Render email templates
                    html_message = render_to_string('custodians/email/verification_email.html', context)
                    text_message = render_to_string('custodians/email/verification_email.txt', context)
                    
                    # Create and send email
                    email = EmailMultiAlternatives(
                        subject='Verify your Keryu account',
                        body=text_message,
                        from_email=None,  # Use DEFAULT_FROM_EMAIL from settings
                        to=[user.email]
                    )
                    email.attach_alternative(html_message, "text/html")
                    email.send()
                    
                    # Get the verification email content for the popup
                    verification_email = PopupEmailBackend.get_verification_email()
                    if verification_email:
                        # Add verification data to the template context
                        return render(request, 'custodians/register.html', {
                            'form': form,
                            'verification_email': verification_email,
                            'verification_url': verification_url,  # Use the properly constructed URL
                        })
                    
                    messages.success(request, 'Registration successful! Please check your email to verify your account.')
                    return redirect('login')
            except Exception as e:
                logger.error(f"Error creating user: {str(e)}")
                messages.error(request, 'An error occurred during registration. Please try again.')
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

def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and email_verification_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Thank you for verifying your email. You can now log in to your account.')
        return redirect('login')
    else:
        messages.error(request, 'The verification link is invalid or has expired.')
        return redirect('login')

@login_required
def dashboard(request):
    # Get subjects based on user role
    if request.user.is_staff:
        subjects = Subject.objects.all().select_related('custodian__user')
        # Get total custodians excluding staff users
        total_custodians = Custodian.objects.exclude(user__is_staff=True).count()
    else:
        subjects = Subject.objects.filter(custodian=request.user.custodian)
        total_custodians = 1
    
    # Calculate statistics
    total_subjects = subjects.count()
    active_subjects = subjects.filter(is_active=True).count()
    
    # Get QR code statistics
    from subjects.models import SubjectQR
    if request.user.is_staff:
        total_qrs = SubjectQR.objects.count()
        active_qrs = SubjectQR.objects.filter(is_active=True).count()
    else:
        total_qrs = SubjectQR.objects.filter(subject__custodian=request.user.custodian).count()
        active_qrs = SubjectQR.objects.filter(subject__custodian=request.user.custodian, is_active=True).count()
    
    # Get recent alarms (last 24 hours)
    last_24h = timezone.now() - timezone.timedelta(hours=24)
    if request.user.is_staff:
        recent_alarms = Alarm.objects.filter(timestamp__gte=last_24h).count()
        total_alarms = Alarm.objects.count()
        response_rate = (Alarm.objects.filter(notification_sent=True).count() / total_alarms * 100) if total_alarms > 0 else 100
    else:
        recent_alarms = Alarm.objects.filter(
            subject__custodian=request.user.custodian,
            timestamp__gte=last_24h
        ).count()
        total_alarms = Alarm.objects.filter(subject__custodian=request.user.custodian).count()
        response_rate = (Alarm.objects.filter(
            subject__custodian=request.user.custodian,
            notification_sent=True
        ).count() / total_alarms * 100) if total_alarms > 0 else 100
    
    # Get recent activities
    if request.user.is_staff:
        recent_activities = Alarm.objects.select_related('subject', 'subject__custodian__user').order_by('-timestamp')[:10]
    else:
        recent_activities = Alarm.objects.filter(
            subject__custodian=request.user.custodian
        ).select_related('subject').order_by('-timestamp')[:10]
    
    # Format activities for display
    formatted_activities = [{
        'subject': activity.subject,
        'event': f"Alarm triggered at {activity.location or 'Unknown Location'}",
        'timestamp': activity.timestamp,
        'status': 'success' if activity.notification_sent else 'warning'
    } for activity in recent_activities]
    
    context = {
        'subjects': subjects,
        'total_subjects': total_subjects,
        'active_subjects': active_subjects,
        'total_custodians': total_custodians,
        'total_qrs': total_qrs,
        'active_qrs': active_qrs,
        'total_alarms': total_alarms,
        'recent_alarms': recent_alarms,
        'response_rate': round(response_rate, 1),
        'recent_activities': formatted_activities,
        'is_admin': request.user.is_staff,
    }
    
    return render(request, 'custodians/dashboard.html', context)

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
