from rest_framework import serializers

from .models import Institution


class InstitutionSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Institution
        fields = [
            'id', 'owner', 'owner_email', 'name', 'type', 'logo', 'description', 'website',
            'country', 'city', 'address', 'contact_email', 'contact_phone',
            'is_active', 'is_verified', 'approval_status', 'rejection_reason',
            'reviewed_at', 'reviewed_by', 'member_count', 'created_at',
        ]
        read_only_fields = [
            'id', 'owner', 'is_active', 'is_verified', 'approval_status',
            'rejection_reason', 'reviewed_at', 'reviewed_by', 'member_count',
            'created_at',
        ]

    def get_member_count(self, obj):
        return obj.members.count()

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Institution name is required.')
        return value
