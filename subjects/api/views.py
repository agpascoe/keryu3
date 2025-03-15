from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from subjects.models import Subject
from .serializers import SubjectSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def subject_list_api(request):
    if request.method == 'GET':
        # Filter subjects based on user's role
        if request.user.is_staff:
            subjects = Subject.objects.all()
        else:
            subjects = Subject.objects.filter(custodian__user=request.user)
        
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Set the custodian to the current user's custodian
        data = request.data.copy()
        data['custodian'] = request.user.custodian.id
        
        serializer = SubjectSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def subject_detail_api(request, pk):
    try:
        if request.user.is_staff:
            subject = Subject.objects.get(pk=pk)
        else:
            subject = Subject.objects.get(pk=pk, custodian__user=request.user)
    except Subject.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SubjectSerializer(subject)
        return Response(serializer.data)

    elif request.method == 'PUT':
        data = request.data.copy()
        data['custodian'] = subject.custodian.id  # Ensure custodian can't be changed
        
        serializer = SubjectSerializer(subject, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        subject.delete()
        return Response(status=status.HTTP_204_NO_CONTENT) 