from rest_framework import serializers
from .models import Institution

class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = ['id','name','slug','institution_type','logo','description','website',
                  'country','city','contact_email','contact_phone','subscription_plan',
                  'max_students','max_tutors','is_active','is_verified','created_at']
        read_only_fields = ['is_verified', 'slug']
