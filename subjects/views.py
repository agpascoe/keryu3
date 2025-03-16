from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, FileResponse
from django.contrib import messages
from django.db.models import Count
from django.contrib.auth.models import User
from .decorators import staff_member_required_403
from .forms import SubjectForm
from django.urls import reverse
import logging
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.conf import settings
import qrcode
import qrcode.image.svg
import uuid
import io
from PIL import Image
from .models import Subject, SubjectQR, Alarm
from .tasks import send_whatsapp_notification
from django.views.decorators.csrf import csrf_exempt

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
    """View to see subject details"""
    # Get the subject and verify ownership
    subject = get_object_or_404(Subject, pk=pk)
    if not request.user.is_staff and subject.custodian.user != request.user:
        return HttpResponse('Permission denied', status=403)
    
    return render(request, 'subjects/subject_detail.html', {
        'subject': subject
    })

@login_required
def subject_edit(request, pk):
    """View to edit a subject"""
    # Get the subject and verify ownership
    subject = get_object_or_404(Subject, pk=pk)
    if not request.user.is_staff and subject.custodian.user != request.user:
        return HttpResponse('Permission denied', status=403)
    
    if request.method == 'POST':
        form = SubjectForm(request.POST, request.FILES, instance=subject)
        if form.is_valid():
            subject = form.save()
            messages.success(request, f'Subject "{subject.name}" was updated successfully.')
            return redirect('subjects:detail', pk=subject.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SubjectForm(instance=subject)
    
    return render(request, 'subjects/subject_form.html', {
        'form': form,
        'subject': subject,
        'title': f'Edit Subject: {subject.name}',
        'submit_text': 'Update'
    })

@login_required
def subject_delete(request, pk):
    """View to delete a subject"""
    # Get the subject and verify ownership
    subject = get_object_or_404(Subject, pk=pk)
    if not request.user.is_staff and subject.custodian.user != request.user:
        return HttpResponse('Permission denied', status=403)
    
    if request.method == 'POST':
        subject_name = subject.name
        subject.delete()
        messages.success(request, f'Subject "{subject_name}" was deleted successfully.')
        return redirect('subjects:list')
    
    return render(request, 'subjects/subject_confirm_delete.html', {
        'subject': subject
    })

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
    """View for managing QR codes"""
    # Get subjects based on user role
    if request.user.is_staff:
        subjects = Subject.objects.all()
    else:
        subjects = Subject.objects.filter(custodian__user=request.user)
    
    # Filter QR codes by subject if specified
    selected_subject = request.GET.get('subject')
    qr_codes = SubjectQR.objects.select_related('subject')
    
    if not request.user.is_staff:
        qr_codes = qr_codes.filter(subject__custodian__user=request.user)
    
    if selected_subject:
        qr_codes = qr_codes.filter(subject_id=selected_subject)
    
    context = {
        'subjects': subjects,
        'qr_codes': qr_codes.order_by('-created_at'),
        'selected_subject': int(selected_subject) if selected_subject else None,
    }
    return render(request, 'subjects/qr_codes.html', context)

@login_required
def generate_qr(request):
    """Generate a new QR code for a subject"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
    
    subject_id = request.POST.get('subject_id')
    activate = request.POST.get('activate') == 'on'
    
    if not subject_id:
        return JsonResponse({'success': False, 'error': 'Subject ID is required'}, status=400)
    
    try:
        # Get subject and verify permissions
        subject = get_object_or_404(Subject, id=subject_id)
        if not request.user.is_staff and subject.custodian.user != request.user:
            return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
        
        # Generate unique UUID
        qr_uuid = str(uuid.uuid4())
        
        # Create QR code instance
        qr = SubjectQR.objects.create(
            subject=subject,
            uuid=qr_uuid,
            is_active=activate
        )
        
        # If activating, deactivate other QR codes
        if activate:
            SubjectQR.objects.filter(subject=subject).exclude(id=qr.id).update(is_active=False)
        
        # Generate QR code image with API endpoint
        api_endpoint = request.build_absolute_uri(
            reverse('subjects:trigger_alarm', args=[qr_uuid])
        )
        
        # Generate QR code
        qr_img = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr_img.add_data(api_endpoint)
        qr_img.make(fit=True)
        
        # Create image
        img = qr_img.make_image(fill_color="black", back_color="white")
        
        # Save image to QR instance
        img_io = io.BytesIO()
        img.save(img_io, format='PNG')
        qr.image.save(f'qr_{qr_uuid}.png', io.BytesIO(img_io.getvalue()))
        
        return JsonResponse({
            'success': True,
            'uuid': qr_uuid,
            'image_url': request.build_absolute_uri(qr.image.url)
        })
        
    except Exception as e:
        logger.error(f"Error generating QR code: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to generate QR code'
        }, status=500)

@login_required
def qr_image(request, uuid):
    """View QR code image"""
    qr = get_object_or_404(SubjectQR, uuid=uuid)
    
    # Check permissions
    if not request.user.is_staff and qr.subject.custodian.user != request.user:
        return HttpResponse('Permission denied', status=403)
    
    # Return image
    if qr.image:
        return FileResponse(qr.image.open(), content_type='image/png')
    
    # Generate image if not exists
    qr_url = request.build_absolute_uri(
        reverse('subjects:scan_qr', args=[uuid])
    )
    img = generate_qr_image(qr_url)
    
    response = HttpResponse(content_type='image/png')
    img.save(response, 'PNG')
    return response

@login_required
def download_qr(request, uuid):
    """Download QR code image"""
    qr = get_object_or_404(SubjectQR, uuid=uuid)
    
    # Check permissions
    if not request.user.is_staff and qr.subject.custodian.user != request.user:
        return HttpResponse('Permission denied', status=403)
    
    # Get or generate image
    if qr.image:
        response = FileResponse(qr.image.open(), content_type='image/png')
    else:
        qr_url = request.build_absolute_uri(
            reverse('subjects:scan_qr', args=[uuid])
        )
        img = generate_qr_image(qr_url)
        response = HttpResponse(content_type='image/png')
        img.save(response, 'PNG')
    
    response['Content-Disposition'] = f'attachment; filename="qr_{uuid}.png"'
    return response

@login_required
@require_POST
def activate_qr(request, uuid):
    """Activate a QR code"""
    qr = get_object_or_404(SubjectQR, uuid=uuid)
    
    # Check permissions
    if not request.user.is_staff and qr.subject.custodian.user != request.user:
        return JsonResponse({
            'success': False,
            'error': 'Permission denied'
        }, status=403)
    
    try:
        # Deactivate other QR codes for this subject
        SubjectQR.objects.filter(subject=qr.subject).update(is_active=False)
        
        # Activate this QR code
        qr.is_active = True
        qr.activated_at = timezone.now()
        qr.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_POST
def deactivate_qr(request, uuid):
    """Deactivate a QR code"""
    qr = get_object_or_404(SubjectQR, uuid=uuid)
    
    # Check permissions
    if not request.user.is_staff and qr.subject.custodian.user != request.user:
        return JsonResponse({
            'success': False,
            'error': 'Permission denied'
        }, status=403)
    
    try:
        qr.is_active = False
        qr.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
@require_POST
def delete_qr(request, uuid):
    """Delete QR code"""
    qr = get_object_or_404(SubjectQR, uuid=uuid)
    
    # Check permissions
    if not request.user.is_staff and qr.subject.custodian.user != request.user:
        return HttpResponse('Permission denied', status=403)
    
    if request.method == 'POST':
        qr.delete()
        messages.success(request, 'QR code deleted successfully')
        return redirect('subjects:qr_codes')
    
    return HttpResponse('Invalid request method', status=405)

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
    qr = get_object_or_404(SubjectQR, uuid=uuid)
    alarm = None
    
    if qr.is_active:
        # Get location from request if available
        location = None
        if request.method == 'POST':
            location = f"{request.POST.get('lat')},{request.POST.get('lng')}"
        elif request.method == 'GET':
            location = f"{request.GET.get('lat')},{request.GET.get('lng')}"
        
        # Create alarm
        alarm = Alarm.objects.create(
            subject=qr.subject,
            qr_code=qr,
            location=location
        )
        
        # Update QR code last used timestamp
        qr.last_used = timezone.now()
        qr.save()
        
        # Send WhatsApp notification immediately in test mode
        try:
            # Since CELERY_TASK_ALWAYS_EAGER is True, this will execute immediately
            send_whatsapp_notification.delay(alarm.id)
            logger.info(f"WhatsApp notification queued for alarm {alarm.id}")
        except Exception as e:
            logger.error(f"Failed to queue WhatsApp notification for alarm {alarm.id}: {e}")
    
    # Return JSON response for API requests
    if request.content_type == 'application/json' or request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'status': 'success' if qr.is_active else 'error',
            'message': 'Alarm triggered successfully' if qr.is_active else 'QR code is not active',
            'alarm_id': alarm.id if alarm else None
        })
    
    # Return HTML response for browser requests
    return render(request, 'subjects/scan_result.html', {
        'qr': qr,
        'alarm': alarm
    })

@require_POST
def trigger_alarm(request, uuid):
    """API endpoint for triggering an alarm from a QR code scan"""
    qr = get_object_or_404(SubjectQR, uuid=uuid)
    
    # Return HTML response for browser requests
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'subjects/test_alarm.html', {'qr': qr})
    
    # For API requests, continue with JSON response
    if not qr.is_active:
        return JsonResponse({
            'status': 'error',
            'message': 'This QR code is not active'
        }, status=400)
    
    # Get location from request if available
    location = None
    if request.POST.get('lat') and request.POST.get('lng'):
        location = f"{request.POST.get('lat')},{request.POST.get('lng')}"
    
    # Create alarm with test flag
    alarm = Alarm.objects.create(
        subject=qr.subject,
        qr_code=qr,
        location=location,
        notification_status='TEST'  # Mark as test alarm
    )
    
    # Update QR code last used timestamp
    qr.last_used = timezone.now()
    qr.save()
    
    # Queue WhatsApp notification
    try:
        send_whatsapp_notification.delay(alarm.id)
    except Exception as e:
        logger.error(f"Failed to queue WhatsApp notification for alarm {alarm.id}: {e}")
    
    return JsonResponse({
        'status': 'success',
        'message': 'Test alarm triggered successfully'
    })

@login_required
def print_qr(request):
    """Print QR code page"""
    uuid = request.GET.get('uuid')
    if not uuid:
        return HttpResponse('QR code UUID is required', status=400)
    
    qr = get_object_or_404(SubjectQR, uuid=uuid)
    
    # Check permissions
    if not request.user.is_staff and qr.subject.custodian.user != request.user:
        return HttpResponse('Permission denied', status=403)
    
    return render(request, 'subjects/print_qr.html', {
        'qr': qr
    })

@login_required
def assign_qr(request):
    """Assign QR code to a subject"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)
    
    qr_id = request.POST.get('qr_id')
    subject_id = request.POST.get('subject_id')
    
    if not qr_id or not subject_id:
        return JsonResponse({'success': False, 'error': 'QR ID and Subject ID are required'}, status=400)
    
    try:
        qr = get_object_or_404(SubjectQR, id=qr_id)
        subject = get_object_or_404(Subject, id=subject_id)
        
        # Check permissions
        if not request.user.is_staff:
            if qr.subject and qr.subject.custodian.user != request.user:
                return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
            if subject.custodian.user != request.user:
                return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
        
        # Assign subject to QR
        qr.subject = subject
        qr.save()
        
        return JsonResponse({
            'success': True,
            'message': f'QR code assigned to {subject.name}'
        })
        
    except Exception as e:
        logger.error(f"Error assigning QR code: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to assign QR code'
        }, status=500)

@login_required
def user_subject_list(request):
    """Regular user view to list their subjects"""
    subjects = Subject.objects.filter(custodian__user=request.user)
    stats = {
        'total_subjects': subjects.count(),
        'active_subjects': subjects.filter(is_active=True).count()
    }
    return render(request, 'subjects/subject_list.html', {
        'subjects': subjects,
        'stats': stats
    })
