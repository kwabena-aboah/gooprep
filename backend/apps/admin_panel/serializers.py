from django.contrib.auth import get_user_model
from rest_framework import serializers


User = get_user_model()


class ReferralSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'full_name', 'email', 'role', 'phone', 'city',
            'avatar_url', 'referrer_name', 'referrer_notes', 'date_joined',
        ]

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.email

    def get_avatar_url(self, obj):
        return obj.get_avatar_url()
