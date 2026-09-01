from rest_framework import serializers
from .models import TutorProfile, Subject, UserDocument


class UserDocumentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
    doc_label = serializers.CharField(source='get_doc_type_display', read_only=True)

    class Meta:
        model = UserDocument
        fields = ['id', 'doc_type', 'doc_label', 'file_url', 'file_name', 'is_verified', 'uploaded_at']

    def get_file_url(self, obj):
        if not obj.file:
            return ''
        url = obj.file.url
        request = self.context.get('request')
        return request.build_absolute_uri(url) if request else url

    def get_file_name(self, obj):
        return obj.file.name.rsplit('/', 1)[-1] if obj.file else ''

class SubjectSerializer(serializers.ModelSerializer):
    class Meta: model = Subject; fields = ['id','name','slug','icon']

class TutorProfileSerializer(serializers.ModelSerializer):
    full_name     = serializers.SerializerMethodField()
    email         = serializers.SerializerMethodField()
    avatar_url    = serializers.SerializerMethodField()
    city          = serializers.SerializerMethodField()
    country       = serializers.SerializerMethodField()
    subjects_list = serializers.SerializerMethodField()
    phone         = serializers.CharField(source='user.phone', read_only=True, allow_blank=True)
    address       = serializers.CharField(source='user.address', read_only=True, allow_blank=True)
    date_of_birth = serializers.DateField(source='user.date_of_birth', read_only=True, allow_null=True)
    gender        = serializers.CharField(source='user.gender', read_only=True, allow_blank=True)
    verification_documents = serializers.SerializerMethodField()

    class Meta:
        model = TutorProfile
        fields = ['id','user_id','full_name','email','phone','avatar_url','city','country','address','date_of_birth','gender',
                  'headline','bio','years_experience','hourly_rate','teaching_style',
                  'trial_lesson_enabled','trial_lesson_price','instant_book','slug',
                  'average_rating','total_reviews','total_lessons','total_students',
                  'response_time','min_notice_hours','max_daily_bookings','booking_buffer_minutes',
                  'is_featured','is_top_rated','approval_status',
                  'subjects_list','education','certifications','intro_video_url','identity_document_type','verification_documents',
                  'total_earnings','pending_payout','total_paid_out','availability',
                  'blocked_dates','packages']

    def get_full_name(self, obj): return obj.user.get_full_name()
    def get_email(self, obj):     return obj.user.email
    def get_avatar_url(self, obj): return obj.user.get_avatar_url()
    def get_city(self, obj):      return obj.user.city
    def get_country(self, obj):   return obj.user.country
    def get_subjects_list(self, obj):
        return [{'id': s.id, 'name': s.name, 'slug': s.slug} for s in obj.subjects.all()]

    def get_verification_documents(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_staff:
            return []
        return UserDocumentSerializer(
            obj.user.verification_documents.all(), many=True, context=self.context
        ).data

        if not request or not request.user.is_staff:
            return []
        return UserDocumentSerializer(
            obj.user.verification_documents.all(), many=True, context=self.context
        ).data
