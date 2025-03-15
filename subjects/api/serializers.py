from rest_framework import serializers
from subjects.models import Subject

class SubjectSerializer(serializers.ModelSerializer):
    custodian_name = serializers.CharField(source='custodian.user.get_full_name', read_only=True)
    
    class Meta:
        model = Subject
        fields = [
            'id', 'name', 'date_of_birth', 'gender', 'medical_conditions',
            'allergies', 'medications', 'doctor_name', 'doctor_phone',
            'doctor_address', 'doctor_speciality', 'photo', 'is_active',
            'custodian', 'custodian_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at'] 