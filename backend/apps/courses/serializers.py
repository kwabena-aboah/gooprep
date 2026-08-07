from rest_framework import serializers
from .models import GroupClass

class GroupClassSerializer(serializers.ModelSerializer):
    tutor_name = serializers.SerializerMethodField()
    subject_name = serializers.SerializerMethodField()
    enrolled = serializers.SerializerMethodField()
    class Meta:
        model = GroupClass
        fields = ['id','title','description','level','tutor_name','subject_name',
                  'start_time','duration_minutes','max_students','enrolled','price','is_active']
    def get_tutor_name(self, obj):   return obj.tutor.get_full_name()
    def get_subject_name(self, obj): return obj.subject.name if obj.subject else ''
    def get_enrolled(self, obj):     return obj.enrollments.count()