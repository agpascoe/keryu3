from django.shortcuts import render
from django.http import HttpResponse

def alarm_list(request):
    return HttpResponse("Alarm list view - Coming soon!")

def alarm_create(request):
    return HttpResponse("Alarm create view - Coming soon!")

def alarm_detail(request, pk):
    return HttpResponse(f"Alarm detail view for ID {pk} - Coming soon!")

def alarm_edit(request, pk):
    return HttpResponse(f"Alarm edit view for ID {pk} - Coming soon!")

def alarm_delete(request, pk):
    return HttpResponse(f"Alarm delete view for ID {pk} - Coming soon!")

def notifications(request):
    return HttpResponse("Notifications view - Coming soon!")
