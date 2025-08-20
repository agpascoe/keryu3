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
from core.messaging import MessageService
from django.views.decorators.csrf import csrf_protect
from django.contrib.sessions.backends.db import SessionStore
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
            user = None
            
            try:
                # Ensure we have a valid session
                if not request.session.session_key:
                    request.session.create()
                
                # Wrap everything in a transaction to ensure atomicity
                with transaction.atomic():
                    # Create user but don't activate yet
                    user = form.save(commit=False)
                    user.is_active = False
                    user.save()
                    
                    # Update custodian profile with string representation of phone number
                    phone_str = form.cleaned_data['phone_number']
                    user.custodian.phone_number = phone_str
                    user.custodian.save()
                    
                    # Generate verification code
                    verification_code = user.custodian.generate_verification_code()
                    
                    # Send verification code via configured messaging service
                    message_service = MessageService()
                    logger.debug(f"Attempting to send verification code to: {phone_str}")
                    message = f"Your Keryu verification code is: {verification_code}"
                    result = message_service.send_message(
                        to_number=phone_str,
                        message=message
                    )
                    logger.debug(f"Message service result: {result}")
                    
                    if result['status'] != 'success':
                        raise Exception(f"Failed to send verification code: {result.get('error', 'Unknown error')}")

                    # Store registration data in session
                    registration_data = {
                        'user_id': user.id,
                        'email': user.email,
                        'phone': phone_str,
                        'timestamp': timezone.now().isoformat(),
                    }
                    
                    # Save to session and ensure it persists
                    request.session['pending_registration'] = registration_data
                    request.session.modified = True
                    request.session.save()
                    
                    logger.debug(f"Stored registration data in session: {registration_data}")
                    logger.debug(f"Session key: {request.session.session_key}")
                    
                    # Create response with session cookie
                    response = redirect('custodians:verify_phone')
                    response.set_cookie('registration_pending', 'true', max_age=900)  # 15 minutes
                    return response
                    
            except Exception as e:
                logger.error(f"Error during registration: {str(e)}", exc_info=True)
                # If user was created but process failed, clean up
                if user and user.id:
                    try:
                        user.delete()
                    except Exception as del_e:
                        logger.error(f"Error cleaning up user after failed registration: {str(del_e)}")
                
                messages.error(request, 'An error occurred during registration. Please try again.')
                if 'phone_number' in str(e):
                    messages.error(request, 'This phone number is already registered.')
                if 'username' in str(e):
                    messages.error(request, 'This username is already taken.')
                if 'email' in str(e):
                    messages.error(request, 'This email is already registered.')
                if 'verification code' in str(e):
                    messages.error(request, str(e))
                if 'session' in str(e):
                    messages.error(request, 'Session error occurred. Please try again.')
                return render(request, 'custodians/register.html', {'form': form})
        else:
            logger.debug(f"Form validation errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustodianRegistrationForm()
    
    return render(request, 'custodians/register.html', {'form': form})

@csrf_protect
def verify_phone(request):
    # Try to get registration data from session
    pending_data = request.session.get('pending_registration')
    has_pending_cookie = request.COOKIES.get('registration_pending') == 'true'
    
    if not pending_data or not has_pending_cookie:
        logger.error("No registration data found in session")
        messages.error(request, 'Registration session expired. Please try registering again.')
        return redirect('custodians:register')
    
    try:
        # Ensure we have valid registration data
        if 'user_id' not in pending_data:
            raise ValueError("Invalid registration data")
            
        try:
            user = User.objects.get(id=pending_data['user_id'])
            logger.debug(f"Found user for verification: {user.email}")
        except User.DoesNotExist:
            logger.error(f"User not found for ID: {pending_data.get('user_id')}")
            # Clean up session data
            request.session.pop('pending_registration', None)
            response = redirect('custodians:register')
            response.delete_cookie('registration_pending')
            messages.error(request, 'Invalid registration session. Please try again.')
            return response
            
        if request.method == 'POST':
            verification_code = request.POST.get('verification_code')
            logger.debug(f"Received verification code for user {user.email}")
            
            try:
                if user.custodian.verify_phone_code(verification_code):
                    # Verification successful
                    user.is_active = True
                    user.save()
                    logger.debug(f"Phone verified successfully for user {user.email}")
                    
                    # Clean up session and log in user
                    request.session.pop('pending_registration', None)
                    login(request, user)
                    
                    # Create response and clean up cookie
                    response = redirect('custodians:custodian_dashboard')
                    response.delete_cookie('registration_pending')
                    messages.success(request, 'Phone verified successfully! Welcome to Keryu.')
                    return response
                else:
                    logger.warning(f"Invalid verification code attempt for user {user.email}")
                    messages.error(request, 'Invalid verification code. Please try again.')
            except Exception as e:
                logger.error(f"Error during phone verification: {str(e)}", exc_info=True)
                messages.error(request, 'An error occurred during verification. Please try again.')
                
        return render(request, 'custodians/verify_phone.html')
        
    except Exception as e:
        logger.error(f"Unexpected error in verify_phone: {str(e)}", exc_info=True)
        messages.error(request, 'An unexpected error occurred. Please try registering again.')
        # Clean up session data
        request.session.pop('pending_registration', None)
        response = redirect('custodians:register')
        response.delete_cookie('registration_pending')
        return response

@require_POST
def resend_verification(request):
    # Ensure we have a valid session
    if not request.session.session_key:
        return JsonResponse({'success': False, 'error': 'Session expired'})
        
    pending_data = request.session.get('pending_registration')
    if not pending_data:
        return JsonResponse({'success': False, 'error': 'Registration session expired'})
        
    try:
        user = User.objects.get(id=pending_data['user_id'])
        verification_code = user.custodian.generate_verification_code()
        
        # Send new verification code
        message_service = MessageService()
        message = f"Your Keryu verification code is: {verification_code}"
        result = message_service.send_message(
            to_number=str(user.custodian.phone_number),
            message=message
        )
        
        if result['status'] == 'success':
            # Update session
            request.session.modified = True
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Failed to send verification code'})
            
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Invalid registration session'})

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
    formatted_activities = []
    for activity in recent_activities:
        location = activity.location if activity.location else 'Unknown Location'
        # Remove None,None from location string
        if location == 'None,None':
            location = 'Unknown Location'
            
        formatted_activities.append({
            'subject': activity.subject,
            'event': f"Alarm triggered at {location}",
            'timestamp': activity.timestamp,
            'status': activity.notification_status or 'PENDING'  # Ensure we always have a valid status
        })
    
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
            messages.success(request, 'Yu added successfully!')
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
            messages.success(request, 'Yu updated successfully!')
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
        messages.success(request, 'Yu deleted successfully!')
        return redirect('custodians:subject_list')
    return render(request, 'custodians/subject_confirm_delete.html', {'subject': subject})

@login_required
def subject_detail(request, pk):
    subject = get_object_or_404(Subject, pk=pk, custodian=request.user.custodian)
    return render(request, 'custodians/subject_detail.html', {'subject': subject})

@login_required
def profile(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'contact_info':
            profile_form = CustodianProfileForm(request.POST, instance=request.user.custodian)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Your contact information was successfully updated!')
                return redirect('custodians:custodian_profile')
            user_form = CustodianUpdateForm(instance=request.user)  # For template rendering
            
        elif form_type == 'account_settings':
            user_form = CustodianUpdateForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Your account settings were successfully updated!')
                return redirect('custodians:custodian_profile')
            profile_form = CustodianProfileForm(instance=request.user.custodian)  # For template rendering
            
        else:
            messages.error(request, 'Invalid form submission.')
            return redirect('custodians:custodian_profile')
            
    else:
        user_form = CustodianUpdateForm(instance=request.user)
        profile_form = CustodianProfileForm(instance=request.user.custodian)
    
    return render(request, 'custodians/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })
