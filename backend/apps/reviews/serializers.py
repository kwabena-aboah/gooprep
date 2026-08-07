from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    reviewer_name   = serializers.SerializerMethodField()
    reviewer_avatar = serializers.SerializerMethodField()
    class Meta:
        model = Review
        fields = ['id','rating','content','reviewer_name','reviewer_avatar',
                  'communication_rating','expertise_rating','punctuality_rating',
                  'would_recommend','tutor_response','is_approved','created_at']
    def get_reviewer_name(self, obj):   return obj.reviewer.get_full_name()
    def get_reviewer_avatar(self, obj): return obj.reviewer.get_avatar_url()