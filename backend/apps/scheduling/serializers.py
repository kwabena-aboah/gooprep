from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Lesson


User = get_user_model()


class LessonSerializer(serializers.ModelSerializer):
    tutor_id = serializers.ReadOnlyField(source="tutor.id")
    student_id = serializers.ReadOnlyField(source="student.id")
    subject_id = serializers.ReadOnlyField(source="subject.id")

    tutor_name = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()
    subject_name = serializers.SerializerMethodField()

    tutor_avatar = serializers.SerializerMethodField()
    student_avatar = serializers.SerializerMethodField()

    class Meta:
        model = Lesson

        fields = [
            "id",

            # Relationships
            "tutor",
            "student",
            "subject",

            # Relationship IDs
            "tutor_id",
            "student_id",
            "subject_id",

            # Display information
            "tutor_name",
            "student_name",
            "subject_name",
            "tutor_avatar",
            "student_avatar",

            # Lesson
            "lesson_type",
            "status",
            "start_time",
            "end_time",
            "duration_minutes",
            "topic",
            "price",
            "currency",

            # Payment
            "payment_status",

            # Recording
            "record_session",
            "recording_available",
            "recording_url",

            # Review / AI
            "has_review",
            "ai_summary",
            "ai_flashcards",
            "ai_quiz",

            # Meeting
            "bbb_meeting_id",

            # Booking on behalf
            "booked_on_behalf",
            "booker_name",
            "booker_relationship",
            "booker_phone",
            "booker_email",

            # Other
            "notes",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "tutor_id",
            "student_id",
            "subject_id",

            "tutor_name",
            "student_name",
            "subject_name",
            "tutor_avatar",
            "student_avatar",

            "status",
            "payment_status",
            "recording_available",
            "recording_url",
            "has_review",
            "ai_summary",
            "ai_flashcards",
            "ai_quiz",
            "bbb_meeting_id",

            "created_at",
            "updated_at",
        ]

    def get_tutor_name(self, obj):
        if not obj.tutor:
            return ""

        return obj.tutor.get_full_name() or obj.tutor.username

    def get_student_name(self, obj):
        if not obj.student:
            return ""

        return obj.student.get_full_name() or obj.student.username

    def get_subject_name(self, obj):
        if not obj.subject:
            return "Tutoring Session"

        return obj.subject.name

    def get_tutor_avatar(self, obj):
        if not obj.tutor:
            return None

        method = getattr(obj.tutor, "get_avatar_url", None)

        if callable(method):
            try:
                return method()
            except Exception:
                return None

        return None

    def get_student_avatar(self, obj):
        if not obj.student:
            return None

        method = getattr(obj.student, "get_avatar_url", None)

        if callable(method):
            try:
                return method()
            except Exception:
                return None

        return None