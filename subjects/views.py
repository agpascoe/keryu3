from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, FileResponse
from django.contrib import messages
from django.db.models import Count, Q
from django.contrib.auth.models import User
from .decorators import staff_member_required_403
from .forms import SubjectForm, SubjectQRForm
from django.urls import reverse
import logging
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.utils import timezone
from django.conf import settings
import qrcode
import qrcode.image.svg
import uuid
import io
from PIL import Image
from .models import Subject, SubjectQR
from alarms.models import Alarm
from alarms.tasks import send_whatsapp_notification
from .tasks import create_test_alarm
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.utils import OperationalError
import time
import os
from io import BytesIO
from django.core.paginator import Paginator
from django.core.cache import cache
from functools import wraps
from django.db import DatabaseError

logger = logging.getLogger(__name__)

@staff_member_required_403
def subject_list(request):
    """Admin view to list all subjects across all custodians"""
    subjects = Subject.objects.all().select_related('custodian__user')
    stats = {
        'total_subjects': subjects.count(),
        'total_custodians': User.objects.filter(custodian__subjects__isnull=False).distinct().count(),
        'active_subjects': subjects.filter(is_active=True).count()
    }
    return render(request, 'subjects/admin_subject_list.html', {
        'subjects': subjects,
        'stats': stats
    })

@login_required
def subject_create(request):
    """View to create a new subject"""
    if request.method == 'POST':
        form = SubjectForm(request.POST, request.FILES)
        logger.debug(f"Form data: {request.POST}")
        if form.is_valid():
            subject = form.save(commit=False)
            subject.custodian = request.user.custodian  # Set the current user as custodian
            subject.save()
            messages.success(request, f'Subject "{subject.name}" was created successfully.')
            return redirect('subjects:detail', pk=subject.pk)
        else:
            logger.debug(f"Form errors: {form.errors}")
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SubjectForm()
    
    return render(request, 'subjects/subject_form.html', {
        'form': form,
        'title': 'Add New Subject',
        'submit_text': 'Create'
    })

@login_required
def subject_detail(request, pk):
    """View to show subject details"""
    if request.user.is_staff:
        subject = get_object_or_404(Subject, pk=pk)
    else:
        subject = get_object_or_404(Subject, pk=pk, custodian=request.user.custodian)
    return render(request, 'subjects/subject_detail.html', {'subject': subject})

@login_required
def subject_edit(request, pk):
    """View to edit a subject"""
    if request.user.is_staff:
        subject = get_object_or_404(Subject, pk=pk)
    else:
        subject = get_object_or_404(Subject, pk=pk, custodian=request.user.custodian)
    
    if request.method == 'POST':
        form = SubjectForm(request.POST, request.FILES, instance=subject)
        if form.is_valid():
            subject = form.save()
            messages.success(request, f'Subject "{subject.name}" was updated successfully.')
            return redirect('subjects:detail', pk=subject.pk)
    else:
        form = SubjectForm(instance=subject)
    
    return render(request, 'subjects/subject_form.html', {
        'form': form,
        'subject': subject,
        'is_edit': True
    })

@login_required
def subject_delete(request, pk):
    """View to delete a subject"""
    if request.user.is_staff:
        subject = get_object_or_404(Subject, pk=pk)
    else:
        subject = get_object_or_404(Subject, pk=pk, custodian=request.user.custodian)
    
    if request.method == 'POST':
        subject.delete()
        messages.success(request, f'Subject "{subject.name}" was deleted successfully.')
        return redirect('subjects:list')
    
    return render(request, 'subjects/subject_confirm_delete.html', {'subject': subject})

@staff_member_required_403
def subject_stats(request):
    """Admin view for subject statistics"""
    stats = {
        'total_subjects': Subject.objects.count(),
        'subjects_by_gender': Subject.objects.values('gender').annotate(count=Count('id')),
        'subjects_by_custodian': Subject.objects.values('custodian__user__username').annotate(count=Count('id')),
        'active_subjects': Subject.objects.filter(is_active=True).count(),
    }
    return render(request, 'subjects/admin_stats.html', {'stats': stats})

@login_required
def qr_codes(request):
    """List QR codes for subjects."""
    # Get the subject ID from query parameters
    subject_id = request.GET.get('subject')
    
    # Base queryset
    qr_codes = SubjectQR.objects.select_related('subject').filter(
        subject__custodian=request.user.custodian
    )
    
    # Filter by subject if specified
    if subject_id:
        qr_codes = qr_codes.filter(subject_id=subject_id)
    
    # Get all subjects for the filter dropdown
    subjects = Subject.objects.filter(custodian=request.user.custodian)
    
    # Add scan URLs for each QR code
    for qr in qr_codes:
        qr.scan_url = request.build_absolute_uri(reverse('subjects:scan_qr', args=[qr.uuid]))
    
    context = {
        'qr_codes': qr_codes,
        'subjects': subjects,
        'selected_subject': subject_id
    }
    
    return render(request, 'subjects/qr_codes.html', context)

@login_required
def generate_qr(request):
    """Generate a new QR code for a subject."""
    if request.method == 'POST':
        try:
            subject_id = request.POST.get('subject_id')
            if not subject_id:
                error_msg = 'Subject ID is required'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': error_msg
                    }, status=400)
                messages.error(request, error_msg)
                return redirect('subjects:qr_codes')

            subject = get_object_or_404(Subject, id=subject_id, custodian=request.user.custodian)
            
            # Generate QR code
            qr = SubjectQR.objects.create(
                subject=subject,
                uuid=uuid.uuid4(),
                is_active=True  # This will deactivate other QR codes
            )
            
            success_msg = 'QR code generated successfully'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                messages.success(request, success_msg)  # Add message even for AJAX
                return JsonResponse({
                    'success': True,
                    'message': success_msg,
                    'uuid': str(qr.uuid)
                })
            
            messages.success(request, success_msg)
            return redirect('subjects:qr_codes')
            
        except Subject.DoesNotExist:
            error_msg = 'Subject not found'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                messages.error(request, error_msg)  # Add message even for AJAX
                return JsonResponse({
                    'success': False,
                    'error': error_msg
                }, status=404)
            messages.error(request, error_msg)
            return redirect('subjects:qr_codes')
        except Exception as e:
            logger.error(f"Error generating QR code: {str(e)}")
            error_msg = 'Failed to generate QR code'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                messages.error(request, error_msg)  # Add message even for AJAX
                return JsonResponse({
                    'success': False,
                    'error': error_msg
                }, status=500)
            messages.error(request, error_msg)
            return redirect('subjects:qr_codes')
    
    return redirect('subjects:qr_codes')

@login_required
def qr_image(request, uuid):
    """Generate and return a QR code image."""
    qr = get_object_or_404(SubjectQR, uuid=uuid)
    
    # Check if user has permission to view this QR code
    if qr.subject.custodian != request.user.custodian:
        return HttpResponse(status=403)
    
    # Generate QR code if it doesn't exist
    if not qr.image:
        # Create QR code instance
        qr_code = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Add the URL data
        url = request.build_absolute_uri(reverse('subjects:scan_qr', args=[uuid]))
        qr_code.add_data(url)
        qr_code.make(fit=True)
        
        # Create the image
        img = qr_code.make_image(fill_color="black", back_color="white")
        
        # Save to BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        
        # Save to model
        image_name = f'qr_{uuid}.png'
        qr.image.save(image_name, buffer, save=True)
    
    # Return the image
    response = HttpResponse(content_type='image/png')
    qr.image.open()
    response.write(qr.image.read())
    qr.image.close()
    return response

@login_required
def download_qr(request, uuid):
    """Download a QR code image."""
    qr = get_object_or_404(SubjectQR, uuid=uuid)
    
    # Check if user has permission to download this QR code
    if qr.subject.custodian != request.user.custodian:
        return HttpResponse(status=403)
    
    # Generate QR code if it doesn't exist
    if not qr.image:
        qr_image(request, uuid)
    
    # Prepare response
    response = HttpResponse(content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="qr_{uuid}.png"'
    
    # Write image to response
    qr.image.open()
    response.write(qr.image.read())
    qr.image.close()
    
    return response

@login_required
@require_POST
def activate_qr(request, uuid):
    """Activate a QR code."""
    qr = get_object_or_404(SubjectQR, uuid=uuid)
    
    # Check if user has permission to activate this QR code
    if qr.subject.custodian != request.user.custodian:
        return HttpResponse(status=403)
    
    qr.is_active = True
    qr.save()  # This will deactivate other QR codes
    
    messages.success(request, 'QR code activated successfully.')
    return redirect('qr_codes')

@login_required
@require_POST
def deactivate_qr(request, uuid):
    """Deactivate a QR code."""
    qr = get_object_or_404(SubjectQR, uuid=uuid)
    
    # Check if user has permission to deactivate this QR code
    if qr.subject.custodian != request.user.custodian:
        return HttpResponse(status=403)
    
    qr.is_active = False
    qr.save()
    
    messages.success(request, 'QR code deactivated successfully.')
    return redirect('qr_codes')

@login_required
@require_POST
def delete_qr(request, uuid):
    """Delete a QR code."""
    qr = get_object_or_404(SubjectQR, uuid=uuid)
    
    # Check if user has permission to delete this QR code
    if qr.subject.custodian != request.user.custodian:
        return HttpResponse(status=403)
    
    qr.delete()
    messages.success(request, 'QR code deleted successfully.')
    return redirect('qr_codes')

def generate_qr_image(url):
    """Helper function to generate QR code image"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    return qr.make_image(fill_color="black", back_color="white")

@csrf_exempt
def scan_qr(request, uuid):
    """Handle QR code scanning and create alarm if active"""
    try:
        with transaction.atomic():
            # Get QR with lock to prevent race conditions
            qr = get_object_or_404(SubjectQR.objects.select_for_update(nowait=True), uuid=uuid)
            
            if not qr.is_active:
                return JsonResponse({
                    'status': 'error',
                    'message': 'QR code is not active',
                    'alarm_id': None
                })

            # Check for recent alarms to prevent duplicates
            recent_alarm = Alarm.objects.filter(
                qr_code=qr,
                timestamp__gte=timezone.now() - timezone.timedelta(minutes=1)
            ).first()

            if recent_alarm:
                logger.info(f"Recent alarm exists for QR {uuid}, returning existing alarm {recent_alarm.id}")
                return JsonResponse({
                    'status': 'success',
                    'message': 'Recent alarm exists',
                    'alarm_id': recent_alarm.id
                })

            # Get location from request if available
            location = None
            if request.method == 'POST':
                location = f"{request.POST.get('lat')},{request.POST.get('lng')}"
            elif request.method == 'GET':
                location = f"{request.GET.get('lat')},{request.GET.get('lng')}"
            
            # Create alarm with proper status
            alarm = Alarm.objects.create(
                subject=qr.subject,
                qr_code=qr,
                location=location,
                notification_status='PENDING',
                notification_attempts=0,
                timestamp=timezone.now(),
                is_test=False  # Regular scan is not a test
            )
            
            # Update QR code last used timestamp
            qr.last_used = timezone.now()
            qr.save(update_fields=['last_used'])
            
            # Schedule notification after transaction commits
            transaction.on_commit(lambda: send_whatsapp_notification.delay(alarm.id, is_test=False))
            
            logger.info(f"Created new alarm {alarm.id} for QR {uuid}")
            
            # Return JSON response for API requests
            if request.content_type == 'application/json' or request.headers.get('Accept') == 'application/json':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Alarm triggered successfully',
                    'alarm_id': alarm.id
                })
            
            # Return HTML response for browser requests
            return render(request, 'subjects/scan_result.html', {
                'qr': qr,
                'alarm': alarm
            })
            
    except DatabaseError as e:
        logger.error(f"Database error in scan_qr: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'System is busy, please try again in a moment',
            'alarm_id': None
        }, status=503)

def prevent_duplicate_submission(timeout=5):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if request.method == "POST":
                # Create a unique key based on user, URL, and QR UUID
                cache_key = f"submission:{request.path}:{kwargs.get('uuid', '')}"
                if cache.get(cache_key):
                    return JsonResponse({"error": "Please wait before retrying"}, status=429)
                cache.set(cache_key, True, timeout)
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator

@require_http_methods(["GET", "POST"])
@prevent_duplicate_submission(timeout=5)
def trigger_qr(request, uuid):
    """View to trigger a QR code scan"""
    try:
        with transaction.atomic():
            # Get QR code with select_for_update to prevent race conditions
            qr = get_object_or_404(SubjectQR.objects.select_for_update(nowait=True), uuid=uuid)
            
            if request.method == "POST":
                # Check if there's a recent pending alarm for this QR code
                recent_alarm = Alarm.objects.filter(
                    qr_code=qr,
                    timestamp__gte=timezone.now() - timezone.timedelta(minutes=1)
                ).first()

                if recent_alarm:
                    logger.info(f"Recent alarm exists for QR {uuid}, returning existing alarm {recent_alarm.id}")
                    return JsonResponse({"status": "success", "alarm_id": recent_alarm.id})

                # Create alarm with transaction
                alarm = Alarm.objects.create(
                    subject=qr.subject,
                    qr_code=qr,
                    is_test=True,
                    notification_status='PENDING',
                    notification_attempts=0,
                    timestamp=timezone.now()
                )
                
                # Schedule notification after transaction commits
                transaction.on_commit(lambda: send_whatsapp_notification.delay(alarm.id, is_test=True))
                
                logger.info(f"Created new test alarm {alarm.id} for QR {uuid}")
                return JsonResponse({"status": "success", "alarm_id": alarm.id})
            
            return render(request, 'subjects/qr_trigger.html', {'qr': qr})
            
    except DatabaseError as e:
        # Log the error and return a user-friendly message
        logger.error(f"Database error in trigger_qr: {str(e)}")
        return JsonResponse(
            {"error": "System is busy, please try again in a moment"},
            status=503
        )

@login_required
def print_qr(request, uuid=None):
    """View to print a QR code"""
    # If no UUID provided, check query parameters
    if uuid is None:
        uuid = request.GET.get('uuid')
        if not uuid:
            return JsonResponse({
                'success': False,
                'error': 'UUID is required'
            }, status=400)
    
    try:
        # Get QR code and verify ownership
        qr = get_object_or_404(SubjectQR, 
                             uuid=uuid, 
                             subject__custodian=request.user.custodian)
        
        # Render print template
        return render(request, 'subjects/print_qr.html', {
            'qr': qr,
            'qr_image_url': request.build_absolute_uri(
                reverse('subjects:qr_image', args=[qr.uuid])
            )
        })
        
    except SubjectQR.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'QR code not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error printing QR code: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to print QR code'
        }, status=500)

@login_required
@require_http_methods(["GET", "POST"])
def assign_qr(request, uuid=None):
    """View to assign QR codes to subjects"""
    if request.method == "POST":
        try:
            with transaction.atomic():
                # If UUID is provided, get that specific QR code
                if uuid:
                    qr = get_object_or_404(SubjectQR.objects.select_for_update(), 
                                         uuid=uuid, 
                                         subject__custodian=request.user.custodian)
                    subject_id = request.POST.get('subject')
                    if not subject_id:
                        return JsonResponse({
                            'success': False,
                            'error': 'Subject ID is required'
                        }, status=400)
                else:
                    # Create new QR code for the subject
                    subject_id = request.POST.get('subject')
                    if not subject_id:
                        return JsonResponse({
                            'success': False,
                            'error': 'Subject ID is required'
                        }, status=400)
                    
                    qr = SubjectQR.objects.create(
                        subject_id=subject_id,
                        uuid=uuid.uuid4(),
                        is_active=True
                    )
                
                # Get the subject and verify ownership
                subject = get_object_or_404(Subject, 
                                          id=subject_id, 
                                          custodian=request.user.custodian)
                
                # Update QR code
                qr.subject = subject
                qr.save()
                
                # Return success response
                return JsonResponse({
                    'success': True,
                    'message': 'QR code assigned successfully',
                    'qr_uuid': str(qr.uuid)
                })
                
        except Exception as e:
            logger.error(f"Error assigning QR code: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to assign QR code'
            }, status=500)
    
    # GET request - return the form
    subjects = Subject.objects.filter(custodian=request.user.custodian)
    return render(request, 'subjects/assign_qr.html', {
        'subjects': subjects,
        'qr_uuid': uuid
    })

@login_required
def user_subject_list(request):
    """View to list subjects based on user role"""
    if request.user.is_staff:
        # Admin can see all subjects
        subjects = Subject.objects.all().select_related('custodian__user')
        stats = {
            'total_subjects': subjects.count(),
            'total_custodians': User.objects.filter(custodian__subjects__isnull=False).distinct().count(),
            'active_subjects': subjects.filter(is_active=True).count()
        }
        template = 'subjects/admin_subject_list.html'
    else:
        # Regular users only see their subjects
        subjects = Subject.objects.filter(custodian=request.user.custodian)
        stats = {
            'total_subjects': subjects.count(),
            'active_subjects': subjects.filter(is_active=True).count()
        }
        template = 'subjects/subject_list.html'

    return render(request, template, {
        'subjects': subjects,
        'stats': stats
    })

@login_required
@require_POST
def toggle_qr_status(request, uuid):
    """Simple toggle of QR active status with JSON response"""
    qr = get_object_or_404(SubjectQR, uuid=uuid, subject__custodian=request.user.custodian)
    with transaction.atomic():
        qr.is_active = not qr.is_active
        qr.save()
    return JsonResponse({
        'success': True,
        'is_active': qr.is_active
    })
