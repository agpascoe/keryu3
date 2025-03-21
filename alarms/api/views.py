from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from subjects.models import Subject
from ..models import Alarm
from .serializers import AlarmSerializer
from ..tasks import send_whatsapp_notification
from django.utils import timezone
from django.db.models import Count, Max, Q, FloatField
from django.db.models.functions import Cast, ExtractHour
from datetime import timedelta
import json

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def alarm_list_api(request):
    if request.method == 'GET':
        # Filter alarms based on user's role
        if request.user.is_staff:
            alarms = Alarm.objects.all()
        else:
            alarms = Alarm.objects.filter(subject__custodian__user=request.user)
        
        serializer = AlarmSerializer(alarms, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        data = request.data.copy()
        
        # Ensure the subject belongs to the current user if not staff
        try:
            if request.user.is_staff:
                subject = Subject.objects.get(pk=data.get('subject'))
            else:
                subject = Subject.objects.get(
                    pk=data.get('subject'),
                    custodian__user=request.user
                )
        except Subject.DoesNotExist:
            return Response(
                {'error': 'Invalid subject ID or permission denied'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Add current timestamp if not provided
        if 'timestamp' not in data:
            data['timestamp'] = timezone.now()
            
        # Add IP address if available
        if 'scanned_by_ip' not in data and request.META.get('REMOTE_ADDR'):
            data['scanned_by_ip'] = request.META.get('REMOTE_ADDR')
        
        serializer = AlarmSerializer(data=data)
        if serializer.is_valid():
            alarm = serializer.save()
            
            # Queue notification task
            try:
                send_whatsapp_notification.delay(alarm.id)
            except Exception as e:
                # Log the error but don't prevent alarm creation
                alarm.notification_error = str(e)
                alarm.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
def alarm_detail_api(request, pk):
    try:
        if request.user.is_staff:
            alarm = Alarm.objects.get(pk=pk)
        else:
            alarm = Alarm.objects.get(pk=pk, subject__custodian__user=request.user)
    except Alarm.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AlarmSerializer(alarm)
        return Response(serializer.data)
    elif request.method == 'DELETE':
        # Only staff can delete alarms
        if not request.user.is_staff:
            return Response(
                {'error': 'Only staff members can delete alarms'},
                status=status.HTTP_403_FORBIDDEN
            )
        alarm.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def alarm_statistics_api(request):
    """API endpoint for alarm statistics"""
    try:
        days = int(request.GET.get('days', 30))
        if days <= 0:
            return Response(
                {'error': 'Days parameter must be positive'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except ValueError:
        return Response(
            {'error': 'Invalid days parameter'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
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
        'subject_stats': [],
        'date_stats': [],
        'notifications': {
            'sent': filtered_alarms.filter(notification_sent=True).count(),
            'failed': filtered_alarms.filter(notification_sent=False, notification_error__isnull=False).count(),
            'pending': filtered_alarms.filter(notification_sent=False, notification_error__isnull=True).count(),
        },
        'time_range': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'days': days
        }
    }
    
    # Get subject statistics
    subject_stats = filtered_alarms.values(
        'subject__name',
        'subject__id'
    ).annotate(
        count=Count('id'),
        last_alarm=Max('timestamp'),
        notification_success_rate=Cast(
            Count('id', filter=Q(notification_sent=True)) * 100.0 / Count('id'),
            output_field=FloatField()
        )
    ).order_by('-count')
    data['subject_stats'] = list(subject_stats)
    
    # Get daily statistics
    daily_stats = filtered_alarms.values('timestamp__date').annotate(
        count=Count('id'),
        notifications_sent=Count('id', filter=Q(notification_sent=True)),
        notifications_failed=Count('id', filter=Q(notification_sent=False))
    ).order_by('timestamp__date')
    data['date_stats'] = list(daily_stats)
    
    # Get hourly distribution
    hour_stats = filtered_alarms.annotate(
        hour=ExtractHour('timestamp')
    ).values('hour').annotate(
        count=Count('id')
    ).order_by('hour')
    data['hour_stats'] = list(hour_stats)
    
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def retry_notification_api(request, alarm_id):
    """API endpoint to retry a failed notification"""
    try:
        if request.user.is_staff:
            alarm = Alarm.objects.get(id=alarm_id)
        else:
            alarm = Alarm.objects.get(
                id=alarm_id,
                subject__custodian__user=request.user
            )
    except Alarm.DoesNotExist:
        return Response(
            {'error': 'Alarm not found or permission denied'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if alarm.notification_sent:
        return Response(
            {'error': 'Notification was already sent'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Queue the notification task
        send_whatsapp_notification.delay(alarm.id)
        
        return Response({
            'success': True,
            'message': 'Notification queued for retry'
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 