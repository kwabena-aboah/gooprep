from rest_framework import serializers
from .models import TutorProfile, Subject, TutorFavourite

class SubjectSerializer(serializers.ModelSerializer):
    class Meta: model = Subject; fields = ['id','name','slug','icon']

class TutorProfileSerializer(serializers.ModelSerializer):
    full_name     = serializers.SerializerMethodField()
    email         = serializers.SerializerMethodField()
    avatar_url    = serializers.SerializerMethodField()
    city          = serializers.SerializerMethodField()
    country       = serializers.SerializerMethodField()
    subjects_list = serializers.SerializerMethodField()

    class Meta:
        model = TutorProfile
        fields = ['id','user_id','full_name','email','avatar_url','city','country',
                  'headline','bio','years_experience','hourly_rate','teaching_style',
                  'trial_lesson_enabled','trial_lesson_price','instant_book','slug',
                  'average_rating','total_reviews','total_lessons','total_students',
                  'response_time','is_featured','is_top_rated','approval_status',
                  'subjects_list','education','certifications','intro_video_url',
                  'total_earnings','pending_payout','total_paid_out','availability']

    def get_full_name(self, obj): return obj.user.get_full_name()
    def get_email(self, obj):     return obj.user.email
    def get_avatar_url(self, obj): return obj.user.get_avatar_url()
    def get_city(self, obj):      return obj.user.city
    def get_country(self, obj):   return obj.user.country
    def get_subjects_list(self, obj):
        return [{'id':s.id,'name':s.name,'slug':s.slug} for s in obj.subjects.all()]