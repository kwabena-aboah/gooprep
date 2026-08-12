from rest_framework import serializers
from .models import StudentProfile


class StudentOnboardingSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ['education_level', 'school', 'subjects_interest', 'learning_goals']


class StudentProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = StudentProfile
        fields = [
            'id', 'full_name', 'email', 'education_level', 'school',
            'subjects_interest', 'learning_goals', 'needs_approval',
            'is_approved', 'created_at',
        ]
        read_only_fields = [
            'id', 'full_name', 'email', 'needs_approval',
            'is_approved', 'created_at',
        ]


