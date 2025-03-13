from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib import messages
from custodians.models import Subject
from django.db.models import Count
from django.contrib.auth.models import User
from .decorators import staff_member_required_403
from .forms import SubjectForm
from django.urls import reverse
import logging

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
def qr_codes(request):
    """Admin view to manage QR codes for all subjects"""
    subjects = Subject.objects.filter(is_active=True).select_related('custodian__user')
    return render(request, 'subjects/admin_qr_codes.html', {
        'subjects': subjects
    })
