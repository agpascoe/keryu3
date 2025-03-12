from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET', 'POST'])
def subject_list_api(request):
    return Response({"message": "Subject list API - Coming soon!"})

@api_view(['GET', 'PUT', 'DELETE'])
def subject_detail_api(request, pk):
    return Response({"message": f"Subject detail API for ID {pk} - Coming soon!"}) 