from rest_framework import serializers
from ..models import Alarm, NotificationAttempt
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

class NotificationAttemptSerializer(serializers.ModelSerializer):
    recipient_name = serializers.SerializerMethodField()

    def get_recipient_name(self, obj):
        return f"{obj.recipient.user.first_name} {obj.recipient.user.last_name}".strip()

    class Meta:
        model = NotificationAttempt
        fields = [
            'id', 'alarm', 'recipient', 'recipient_name', 'channel',
            'status', 'sent_at', 'error_message', 'retry_count', 'created_at'
        ]
        read_only_fields = ['sent_at', 'error_message', 'retry_count', 'created_at'] 