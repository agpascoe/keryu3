from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from subjects.models import Subject
from ..models import Alarm, NotificationStatus, NotificationAttempt
from .serializers import AlarmSerializer, NotificationAttemptSerializer
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

class AlarmViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing alarms."""
    serializer_class = AlarmSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter alarms based on user's role."""
        if self.request.user.is_staff:
            return Alarm.objects.all()
        return Alarm.objects.filter(subject__custodian__user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['notification_attempts'] = NotificationAttempt.objects.filter(
            alarm__in=self.get_queryset()
        ).select_related('recipient', 'recipient__user')
        return context

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve an alarm."""
        alarm = self.get_object()
        alarm.resolved_at = timezone.now()
        alarm.resolution_notes = request.data.get('resolution_notes', '')
        alarm.save()
        return Response({'status': 'alarm resolved'})

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get alarm statistics."""
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
        
        alarms = self.get_queryset()
        filtered_alarms = alarms.filter(timestamp__range=[start_date, end_date])
        
        data = {
            'total_alarms': alarms.count(),
            'recent_alarms': filtered_alarms.count(),
            'subject_stats': [],
            'date_stats': [],
            'notifications': {
                'sent': filtered_alarms.filter(notification_status=NotificationStatus.SENT).count(),
                'delivered': filtered_alarms.filter(notification_status=NotificationStatus.DELIVERED).count(),
                'failed': filtered_alarms.filter(notification_status__in=[NotificationStatus.FAILED, NotificationStatus.ERROR]).count(),
                'pending': filtered_alarms.filter(notification_status__in=[NotificationStatus.PENDING, NotificationStatus.PROCESSING]).count(),
            },
            'time_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            }
        }
        
        subject_stats = filtered_alarms.values(
            'subject__name',
            'subject__id'
        ).annotate(
            count=Count('id'),
            last_alarm=Max('timestamp'),
            notification_success_rate=Cast(
                Count('id', filter=Q(notification_status=NotificationStatus.SENT)) * 100.0 / Count('id'),
                output_field=FloatField()
            )
        ).order_by('-count')
        data['subject_stats'] = list(subject_stats)
        
        daily_stats = filtered_alarms.values('timestamp__date').annotate(
            count=Count('id'),
            notifications_sent=Count('id', filter=Q(notification_status=NotificationStatus.SENT)),
            notifications_failed=Count('id', filter=Q(notification_status__in=[NotificationStatus.FAILED, NotificationStatus.ERROR]))
        ).order_by('timestamp__date')
        data['date_stats'] = list(daily_stats)
        
        hour_stats = filtered_alarms.annotate(
            hour=ExtractHour('timestamp')
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('hour')
        data['hour_stats'] = list(hour_stats)
        
        return Response(data)

class NotificationAttemptViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing notification attempts."""
    serializer_class = NotificationAttemptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter notification attempts based on user's role."""
        if self.request.user.is_staff:
            return NotificationAttempt.objects.all()
        return NotificationAttempt.objects.filter(alarm__subject__custodian__user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_sent(self, request, pk=None):
        """Mark a notification attempt as sent."""
        attempt = self.get_object()
        attempt.status = NotificationStatus.SENT
        attempt.save()
        return Response({'status': 'notification marked as sent'})

    @action(detail=True, methods=['post'])
    def mark_failed(self, request, pk=None):
        """Mark a notification attempt as failed."""
        attempt = self.get_object()
        attempt.status = NotificationStatus.FAILED
        attempt.error_message = request.data.get('error_message', '')
        attempt.save()
        return Response({'status': 'notification marked as failed'})

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
            'sent': filtered_alarms.filter(notification_status=NotificationStatus.SENT).count(),
            'delivered': filtered_alarms.filter(notification_status=NotificationStatus.DELIVERED).count(),
            'failed': filtered_alarms.filter(notification_status__in=[NotificationStatus.FAILED, NotificationStatus.ERROR]).count(),
            'pending': filtered_alarms.filter(notification_status__in=[NotificationStatus.PENDING, NotificationStatus.PROCESSING]).count(),
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
            Count('id', filter=Q(notification_status=NotificationStatus.SENT)) * 100.0 / Count('id'),
            output_field=FloatField()
        )
    ).order_by('-count')
    data['subject_stats'] = list(subject_stats)
    
    # Get daily statistics
    daily_stats = filtered_alarms.values('timestamp__date').annotate(
        count=Count('id'),
        notifications_sent=Count('id', filter=Q(notification_status=NotificationStatus.SENT)),
        notifications_failed=Count('id', filter=Q(notification_status__in=[NotificationStatus.FAILED, NotificationStatus.ERROR]))
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
    
    if alarm.notification_status == NotificationStatus.SENT:
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