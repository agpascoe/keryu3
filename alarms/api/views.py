from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from subjects.models import Alarm, Subject
from .serializers import AlarmSerializer
from django.utils import timezone

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
        
        serializer = AlarmSerializer(data=data)
        if serializer.is_valid():
            alarm = serializer.save()
            # Here you might want to trigger notifications
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
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

    elif request.method == 'PUT':
        # Only allow updating certain fields
        data = request.data.copy()
        data['subject'] = alarm.subject.id  # Can't change the subject
        data['timestamp'] = alarm.timestamp  # Can't change the timestamp
        
        serializer = AlarmSerializer(alarm, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        alarm.delete()
        return Response(status=status.HTTP_204_NO_CONTENT) 