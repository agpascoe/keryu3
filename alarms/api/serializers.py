from rest_framework import serializers
from ..models import Alarm
from subjects.models import Subject, SubjectQR

class AlarmSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    custodian_name = serializers.CharField(source='subject.custodian.user.get_full_name', read_only=True)
    qr_code_uuid = serializers.UUIDField(source='qr_code.uuid', read_only=True)
    
    class Meta:
        model = Alarm
        fields = [
            'id', 'subject', 'subject_name', 'custodian_name', 'qr_code', 'qr_code_uuid',
            'timestamp', 'location', 'notification_sent', 'notification_status', 'last_attempt',
            'notification_error', 'notification_attempts', 'whatsapp_message_id', 'is_test'
        ]
        read_only_fields = [
            'timestamp', 'notification_sent', 'notification_status', 'last_attempt',
            'notification_error', 'notification_attempts', 'whatsapp_message_id'
        ] 