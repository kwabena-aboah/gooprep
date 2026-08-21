from rest_framework import serializers
from .models import StudentProfile
from apps.tutors.serializers import UserDocumentSerializer


class StudentOnboardingSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ['education_level', 'school', 'subjects_interest', 'learning_goals', 'identity_document_type']


class StudentProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    verification_documents = serializers.SerializerMethodField()

    def get_verification_documents(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_staff:
            return []
        return UserDocumentSerializer(
            obj.user.verification_documents.all(), many=True, context=self.context
        ).data

    class Meta:
        model = StudentProfile
        fields = [
            'id', 'full_name', 'email', 'education_level', 'school',
            'subjects_interest', 'learning_goals', 'identity_document_type', 'needs_approval', 'verification_documents',
            'is_approved', 'created_at',
        ]
        read_only_fields = [
            'id', 'full_name', 'email', 'needs_approval',
            'is_approved', 'created_at',
        ]


