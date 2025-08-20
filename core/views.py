from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from subjects.models import Subject, SubjectQR
from alarms.models import Alarm


def home(request):
    """Home page view with user progress tracking."""
    context = {}
    
    if request.user.is_authenticated:
        try:
            custodian = request.user.custodian
            
            # Get user's progress data
            user_subjects = Subject.objects.filter(custodian=custodian)
            user_qr_codes = SubjectQR.objects.filter(subject__custodian=custodian)
            user_alarms = Alarm.objects.filter(subject__custodian=custodian)
            
            # Progress tracking
            context.update({
                'has_subjects': user_subjects.exists(),
                'has_qr_codes': user_qr_codes.exists(),
                'has_alarms': user_alarms.exists(),
                'subjects_count': user_subjects.count(),
                'qr_codes_count': user_qr_codes.count(),
                'alarms_count': user_alarms.count(),
            })
            
        except AttributeError:
            # User doesn't have a custodian profile yet
            context.update({
                'has_subjects': False,
                'has_qr_codes': False,
                'has_alarms': False,
                'subjects_count': 0,
                'qr_codes_count': 0,
                'alarms_count': 0,
            })
    
    return render(request, 'home.html', context)