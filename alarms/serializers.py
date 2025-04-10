from rest_framework import serializers
from .models import Alarm, NotificationAttempt
from subjects.models import Subject, SubjectQR

class AlarmSerializer(serializers.ModelSerializer):
    """Serializer for the Alarm model."""
    class Meta:
        model = Alarm
        fields = [
            'id', 'subject', 'qr_code', 'location', 'is_test',
            'notification_status', 'notification_sent', 'notification_error',
            'notification_attempt_count', 'last_attempt', 'whatsapp_message_id',
            'resolved_at', 'resolution_notes', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'notification_status', 'notification_sent', 'notification_error',
            'notification_attempt_count', 'last_attempt', 'whatsapp_message_id',
            'resolved_at', 'created_at', 'updated_at'
        ]

    def validate_subject(self, value):
        """Validate that the subject exists."""
        try:
            # If value is already a Subject instance, return it
            if isinstance(value, Subject):
                return value
            # Otherwise, get the Subject by ID
            return Subject.objects.get(id=value)
        except Subject.DoesNotExist:
            raise serializers.ValidationError("Subject does not exist")
        except (ValueError, AttributeError):
            raise serializers.ValidationError("Invalid subject value")

    def validate_qr_code(self, value):
        """Validate that the QR code exists."""
        try:
            # If value is already a SubjectQR instance, get its ID
            qr_code_id = value.id if isinstance(value, SubjectQR) else value
            return SubjectQR.objects.get(id=qr_code_id)
        except SubjectQR.DoesNotExist:
            raise serializers.ValidationError("QR code does not exist")
        except (ValueError, AttributeError):
            raise serializers.ValidationError("Invalid QR code value")

    def validate_location(self, value):
        """Validate that location is not empty."""
        if not value or value.strip() == '':
            raise serializers.ValidationError("Location cannot be empty")
        return value

    def validate_is_test(self, value):
        """Validate that is_test is a boolean."""
        if not isinstance(value, bool):
            raise serializers.ValidationError("is_test must be a boolean value")
        return value

class NotificationAttemptSerializer(serializers.ModelSerializer):
    """Serializer for the NotificationAttempt model."""
    class Meta:
        model = NotificationAttempt
        fields = [
            'id', 'alarm', 'recipient', 'channel', 'status',
            'sent_at', 'error_message', 'retry_count', 'created_at'
        ]
        read_only_fields = [
            'status', 'sent_at', 'error_message', 'retry_count', 'created_at'
        ] 