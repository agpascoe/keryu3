from django.shortcuts import render
from django.http import HttpResponse

def subject_list(request):
    return HttpResponse("Subject list view - Coming soon!")

def subject_create(request):
    return HttpResponse("Subject create view - Coming soon!")

def subject_detail(request, pk):
    return HttpResponse(f"Subject detail view for ID {pk} - Coming soon!")

def subject_edit(request, pk):
    return HttpResponse(f"Subject edit view for ID {pk} - Coming soon!")

def subject_delete(request, pk):
    return HttpResponse(f"Subject delete view for ID {pk} - Coming soon!")

def qr_codes(request):
    return HttpResponse("QR codes view - Coming soon!")
