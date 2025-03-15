from rest_framework import serializers
from subjects.models import Alarm

class AlarmSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    custodian_name = serializers.CharField(source='subject.custodian.user.get_full_name', read_only=True)
    
    class Meta:
        model = Alarm
        fields = [
            'id', 'subject', 'subject_name', 'custodian_name',
            'qr_code', 'timestamp', 'location',
            'notification_sent', 'notification_error'
        ]
        read_only_fields = ['timestamp', 'notification_sent', 'notification_error'] 