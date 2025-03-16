from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse, FileResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import timedelta
import csv
import xlsxwriter
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from subjects.models import Alarm, Subject, SubjectQR
from .tasks import send_whatsapp_notification
import json
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph

@login_required
def alarm_list(request):
    """View for listing alarms with filtering options"""
    alarms = Alarm.objects.select_related('subject', 'qr_code')
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if date_from:
        alarms = alarms.filter(timestamp__gte=date_from)
    if date_to:
        alarms = alarms.filter(timestamp__lte=date_to)
    
    # Filter by subject
    subject_id = request.GET.get('subject')
    if subject_id:
        alarms = alarms.filter(subject_id=subject_id)
    
    # Filter by notification status
    notification_status = request.GET.get('notification_status')
    if notification_status == 'sent':
        alarms = alarms.filter(notification_sent=True)
    elif notification_status == 'failed':
        alarms = alarms.filter(notification_sent=False)
    
    # Get subjects for filter dropdown
    if request.user.is_staff:
        subjects = Subject.objects.all()
    else:
        subjects = Subject.objects.filter(custodian__user=request.user)

    # Order by most recent first
    alarms = alarms.order_by('-timestamp')

    # Pagination
    paginator = Paginator(alarms, 20)  # Show 20 alarms per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'subjects': subjects,
        'date_from': date_from,
        'date_to': date_to,
        'selected_subject': subject_id,
        'notification_status': notification_status
    }
    return render(request, 'alarms/alarm_list.html', context)

def alarm_create(request):
    return HttpResponse("Alarm create view - Coming soon!")

@login_required
def alarm_detail(request, pk):
    """View for showing alarm details"""
    alarm = get_object_or_404(Alarm, pk=pk)
    return render(request, 'alarms/alarm_detail.html', {'alarm': alarm})

def alarm_edit(request, pk):
    return HttpResponse(f"Alarm edit view for ID {pk} - Coming soon!")

def alarm_delete(request, pk):
    return HttpResponse(f"Alarm delete view for ID {pk} - Coming soon!")

def notifications(request):
    return HttpResponse("Notifications view - Coming soon!")

@login_required
def alarm_statistics(request):
    """View for showing alarm statistics"""
    # Get time range
    days = int(request.GET.get('days', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Get alarms based on user role
    if request.user.is_staff:
        alarms = Alarm.objects.all()
    else:
        alarms = Alarm.objects.filter(subject__custodian__user=request.user)
    
    # Get filtered alarms for the time range
    filtered_alarms = alarms.filter(timestamp__range=[start_date, end_date])
    
    # Calculate statistics
    stats = {
        'total_alarms': alarms.count(),
        'recent_alarms': filtered_alarms.count(),
        'notifications': {
            'sent': filtered_alarms.filter(notification_sent=True).count(),
            'failed': filtered_alarms.filter(notification_sent=False, notification_error__isnull=False).count(),
            'pending': filtered_alarms.filter(notification_sent=False, notification_error__isnull=True).count(),
        }
    }
    
    # Get subject data
    subject_stats = filtered_alarms.values('subject__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Get daily data
    daily_stats = filtered_alarms.values('timestamp__date').annotate(
        count=Count('id')
    ).order_by('timestamp__date')
    
    # Prepare chart data
    chart_data = {
        'subject_labels': [item['subject__name'] for item in subject_stats],
        'subject_data': [item['count'] for item in subject_stats],
        'date_labels': [item['timestamp__date'].strftime('%Y-%m-%d') for item in daily_stats],
        'date_data': [item['count'] for item in daily_stats],
        'notifications': stats['notifications']
    }
    
    return render(request, 'alarms/alarm_statistics.html', {
        'stats': stats,
        'days': days,
        'chart_data': chart_data,
        'total_alarms': stats['total_alarms'],
        'recent_alarms': stats['recent_alarms'],
        'total_subjects': Subject.objects.count() if request.user.is_staff else Subject.objects.filter(custodian__user=request.user).count()
    })

@login_required
def statistics_data(request):
    """AJAX endpoint for statistics data"""
    days = int(request.GET.get('days', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    if request.user.is_staff:
        alarms = Alarm.objects.all()
    else:
        alarms = Alarm.objects.filter(subject__custodian__user=request.user)
    
    # Get filtered data
    filtered_alarms = alarms.filter(timestamp__range=[start_date, end_date])
    
    # Prepare statistics
    data = {
        'total_alarms': alarms.count(),
        'recent_alarms': filtered_alarms.count(),
        'subject_labels': [],
        'subject_data': [],
        'date_labels': [],
        'date_data': [],
        'notifications': {
            'sent': filtered_alarms.filter(notification_sent=True).count(),
            'failed': filtered_alarms.filter(notification_sent=False, notification_error__isnull=False).count(),
            'pending': filtered_alarms.filter(notification_sent=False, notification_error__isnull=True).count(),
        }
    }
    
    # Get subject data
    subject_stats = filtered_alarms.values('subject__name').annotate(
        count=Count('id')
    ).order_by('-count')
    data['subject_labels'] = [item['subject__name'] for item in subject_stats]
    data['subject_data'] = [item['count'] for item in subject_stats]
    
    # Get daily data
    daily_stats = filtered_alarms.values('timestamp__date').annotate(
        count=Count('id')
    ).order_by('timestamp__date')
    data['date_labels'] = [item['timestamp__date'].strftime('%Y-%m-%d') for item in daily_stats]
    data['date_data'] = [item['count'] for item in daily_stats]
    
    return JsonResponse(data)

@login_required
def export_csv(request):
    """Export alarm data as CSV"""
    if request.user.is_staff:
        alarms = Alarm.objects.all()
    else:
        alarms = Alarm.objects.filter(subject__custodian__user=request.user)
    
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="alarms_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'Subject', 'Custodian', 'Location', 'Notification Status'])
    
    for alarm in alarms:
        writer.writerow([
            alarm.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            alarm.subject.name,
            alarm.subject.custodian.user.get_full_name(),
            alarm.location or 'N/A',
            'Sent' if alarm.notification_sent else 'Pending'
        ])
    
    return response

@login_required
def export_alarms_excel(request):
    """Export alarms to Excel file"""
    # Create output
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    
    # Add headers
    headers = ['Date', 'Time', 'Subject', 'Location', 'Notification Status']
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)
    
    # Add data
    alarms = Alarm.objects.select_related('subject').order_by('-timestamp')
    for row, alarm in enumerate(alarms, start=1):
        worksheet.write(row, 0, alarm.timestamp.strftime('%Y-%m-%d'))
        worksheet.write(row, 1, alarm.timestamp.strftime('%H:%M:%S'))
        worksheet.write(row, 2, alarm.subject.name)
        worksheet.write(row, 3, alarm.location or 'N/A')
        worksheet.write(row, 4, 'Sent' if alarm.notification_sent else 'Failed')
    
    workbook.close()
    output.seek(0)
    
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=alarms.xlsx'
    return response

@login_required
def export_alarms_pdf(request):
    """Export alarms to PDF file"""
    # Create response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=alarms.pdf'
    
    # Create PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    
    # Add title
    styles = getSampleStyleSheet()
    elements.append(Paragraph('Alarm Report', styles['Title']))
    
    # Create table data
    data = [['Date', 'Time', 'Subject', 'Location', 'Notification Status']]
    alarms = Alarm.objects.select_related('subject').order_by('-timestamp')
    
    for alarm in alarms:
        data.append([
            alarm.timestamp.strftime('%Y-%m-%d'),
            alarm.timestamp.strftime('%H:%M:%S'),
            alarm.subject.name,
            alarm.location or 'N/A',
            'Sent' if alarm.notification_sent else 'Failed'
        ])
    
    # Create table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    return response

@staff_member_required
def admin_alarm_dashboard(request):
    """Admin view for system-wide alarm monitoring"""
    alarms = Alarm.objects.all()
    recent_alarms = alarms.filter(timestamp__gte=timezone.now() - timedelta(days=7))
    
    # Get statistics
    stats = {
        'total_alarms': alarms.count(),
        'recent_alarms': recent_alarms.count(),
        'notifications_sent': alarms.filter(notification_sent=True).count(),
        'notifications_failed': alarms.filter(notification_sent=False).count(),
    }
    
    # Get recent alarms for display
    latest_alarms = recent_alarms.select_related('subject', 'qr_code')[:10]
    
    context = {
        'stats': stats,
        'latest_alarms': latest_alarms,
        'now': timezone.now(),  # Add current timestamp for display
    }
    return render(request, 'alarms/admin_dashboard.html', context)

@staff_member_required
@require_POST
def retry_notification(request, alarm_id):
    """Endpoint to retry sending a failed notification"""
    alarm = get_object_or_404(Alarm, id=alarm_id)
    
    if alarm.notification_sent:
        return JsonResponse({
            'success': False,
            'error': 'Notification was already sent'
        })
    
    try:
        # Queue the notification task
        send_whatsapp_notification.delay(alarm.id)
        
        return JsonResponse({
            'success': True,
            'message': 'Notification queued for retry'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
