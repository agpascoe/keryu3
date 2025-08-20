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
            user_yus = Subject.objects.filter(custodian=custodian)
            user_kers = SubjectQR.objects.filter(subject__custodian=custodian)
            user_alarms = Alarm.objects.filter(subject__custodian=custodian)
            
            # Progress tracking
            context.update({
                'has_yus': user_yus.exists(),
                'has_kers': user_kers.exists(),
                'has_alarms': user_alarms.exists(),
                'yus_count': user_yus.count(),
                'kers_count': user_kers.count(),
                'alarms_count': user_alarms.count(),
            })
            
        except AttributeError:
            # User doesn't have a custodian profile yet
            context.update({
                'has_yus': False,
                'has_kers': False,
                'has_alarms': False,
                'yus_count': 0,
                'kers_count': 0,
                'alarms_count': 0,
            })
    
    return render(request, 'home.html', context)