from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET', 'POST'])
def custodian_list_api(request):
    return Response({"message": "Custodian list API - Coming soon!"})

@api_view(['GET', 'PUT', 'DELETE'])
def custodian_detail_api(request, pk):
    return Response({"message": f"Custodian detail API for ID {pk} - Coming soon!"}) 