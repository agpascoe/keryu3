from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET', 'POST'])
def alarm_list_api(request):
    return Response({"message": "Alarm list API - Coming soon!"})

@api_view(['GET', 'PUT', 'DELETE'])
def alarm_detail_api(request, pk):
    return Response({"message": f"Alarm detail API for ID {pk} - Coming soon!"}) 