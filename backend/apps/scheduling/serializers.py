from rest_framework import serializers
from .models import Lesson

class LessonSerializer(serializers.ModelSerializer):
    tutor_name    = serializers.SerializerMethodField()
    student_name  = serializers.SerializerMethodField()
    subject_name  = serializers.SerializerMethodField()
    tutor_avatar  = serializers.SerializerMethodField()
    student_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ['id','tutor_id','student_id','subject_id','tutor_name','student_name',
                  'tutor_avatar','student_avatar','subject_name','lesson_type','status',
                  'start_time','end_time','duration_minutes','topic','price','currency',
                  'payment_status','record_session','recording_available','recording_url',
                  'has_review','ai_summary','ai_flashcards','ai_quiz','bbb_meeting_id',
                  'booked_on_behalf','booker_name','booker_relationship','booker_phone',
                  'booker_email','notes','created_at']

    def get_tutor_name(self, obj):     return obj.tutor.get_full_name()
    def get_student_name(self, obj):   return obj.student.get_full_name()
    def get_subject_name(self, obj):   return obj.subject.name if obj.subject else 'Tutoring Session'
    def get_tutor_avatar(self, obj):   return obj.tutor.get_avatar_url()
    def get_student_avatar(self, obj): return obj.student.get_avatar_url()