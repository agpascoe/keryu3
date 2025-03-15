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

@staff_member_required_403
def subject_create(request):
    """Admin view to create a new subject"""
    if request.method == 'POST':
        form = SubjectForm(request.POST, request.FILES)
        logger.debug(f"Form data: {request.POST}")
        if form.is_valid():
            subject = form.save()
            messages.success(request, f'Subject "{subject.name}" was created successfully.')
            return redirect('subjects:subject_detail', pk=subject.pk)
        else:
            logger.debug(f"Form errors: {form.errors}")
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SubjectForm()
    
    return render(request, 'subjects/admin_subject_form.html', {
        'form': form,
        'title': 'Create Subject',
        'submit_text': 'Create'
    })

@staff_member_required_403
def subject_detail(request, pk):
    """Admin view to see complete subject details"""
    subject = get_object_or_404(Subject, pk=pk)
    return render(request, 'subjects/admin_subject_detail.html', {
        'subject': subject
    })

@staff_member_required_403
def subject_edit(request, pk):
    """Admin view to edit a subject"""
    subject = get_object_or_404(Subject, pk=pk)
    
    if request.method == 'POST':
        form = SubjectForm(request.POST, request.FILES, instance=subject)
        logger.debug(f"Form data: {request.POST}")
        if form.is_valid():
            subject = form.save()
            messages.success(request, f'Subject "{subject.name}" was updated successfully.')
            return redirect('subjects:subject_detail', pk=subject.pk)
        else:
            logger.debug(f"Form errors: {form.errors}")
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SubjectForm(instance=subject)
    
    return render(request, 'subjects/admin_subject_form.html', {
        'form': form,
        'subject': subject,
        'title': f'Edit Subject: {subject.name}',
        'submit_text': 'Update'
    })

@staff_member_required_403
def subject_delete(request, pk):
    """Admin view to delete a subject"""
    subject = get_object_or_404(Subject, pk=pk)
    
    if request.method == 'POST':
        subject_name = subject.name
        subject.delete()
        messages.success(request, f'Subject "{subject_name}" was deleted successfully.')
        return redirect('subjects:subject_list')
    
    return render(request, 'subjects/admin_subject_confirm_delete.html', {
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

@staff_member_required_403
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
@require_POST
def generate_qr(request):
    """Generate a new QR code for a subject"""
    subject_id = request.POST.get('subject_id')
    activate = request.POST.get('activate') == 'on'
    
    # Verify permissions
    subject = get_object_or_404(Subject, id=subject_id)
    if not request.user.is_staff and subject.custodian.user != request.user:
        return JsonResponse({
            'success': False,
            'error': 'Permission denied'
        }, status=403)
    
    try:
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
        img = generate_qr_image(api_endpoint)
        
        # Save image to QR instance
        img_io = io.BytesIO()
        img.save(img_io, format='PNG')
        qr.image.save(f'qr_{qr_uuid}.png', io.BytesIO(img_io.getvalue()))
        
        return JsonResponse({
            'success': True,
            'uuid': qr_uuid
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
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
    """Delete a QR code"""
    qr = get_object_or_404(SubjectQR, uuid=uuid)
    
    # Check permissions
    if not request.user.is_staff and qr.subject.custodian.user != request.user:
        return JsonResponse({
            'success': False,
            'error': 'Permission denied'
        }, status=403)
    
    try:
        qr.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

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
    
    if not qr.is_active:
        return JsonResponse({
            'status': 'error',
            'message': 'This QR code is no longer active'
        }, status=400)
    
    # Get location from request if available
    location = None
    if request.POST.get('lat') and request.POST.get('lng'):
        location = f"{request.POST.get('lat')},{request.POST.get('lng')}"
    
    # Create alarm
    alarm = Alarm.objects.create(
        subject=qr.subject,
        qr_code=qr,
        location=location
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
        'message': 'Alarm triggered successfully'
    })

@login_required
def print_qr(request, uuid):
    """Print view for QR code"""
    qr = get_object_or_404(SubjectQR, uuid=uuid)
    
    # Check permissions
    if not request.user.is_staff and qr.subject.custodian.user != request.user:
        return HttpResponse('Permission denied', status=403)
    
    # Get or generate QR image URL
    if qr.image:
        qr_image_url = qr.image.url
    else:
        # Generate QR code image
        api_endpoint = request.build_absolute_uri(
            reverse('subjects:trigger_alarm', args=[qr.uuid])
        )
        img = generate_qr_image(api_endpoint)
        
        # Save image
        img_io = io.BytesIO()
        img.save(img_io, format='PNG')
        qr.image.save(f'qr_{qr.uuid}.png', io.BytesIO(img_io.getvalue()))
        qr_image_url = qr.image.url
    
    return render(request, 'subjects/print_qr.html', {
        'qr': qr,
        'qr_image_url': qr_image_url
    })
