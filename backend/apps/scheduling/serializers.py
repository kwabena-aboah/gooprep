from django.utils import timezone
from rest_framework import serializers

from .models import Lesson


class LessonSerializer(serializers.ModelSerializer):
    subject_name = serializers.ReadOnlyField()
    tutor_name = serializers.ReadOnlyField()
    student_name = serializers.ReadOnlyField()

    is_upcoming = serializers.SerializerMethodField()
    is_live = serializers.ReadOnlyField()

    bbb_tutor_join_url = serializers.SerializerMethodField()
    bbb_student_join_url = serializers.SerializerMethodField()
    bbb_status = serializers.SerializerMethodField()
    bbb_created_at = serializers.SerializerMethodField()
    bbb_started_at = serializers.SerializerMethodField()
    bbb_ended_at = serializers.SerializerMethodField()
    bbb_recordings = serializers.SerializerMethodField()
    bbb_available = serializers.SerializerMethodField()
    can_join = serializers.SerializerMethodField()

    class Meta:
        model = Lesson

        fields = [
            "id",

            # Participants
            "tutor",
            "student",
            "tutor_name",
            "student_name",

            # Subject
            "subject",
            "subject_name",

            # Lesson
            "lesson_type",
            "status",
            "start_time",
            "end_time",
            "duration_minutes",
            "topic",

            # Payment
            "price",
            "currency",
            "payment_status",

            # BBB
            "bbb_meeting_id",
            "bbb_tutor_join_url",
            "bbb_student_join_url",
            "bbb_status",
            "bbb_created_at",
            "bbb_started_at",
            "bbb_ended_at",

            # Recording
            "record_session",
            "recording_available",
            "recording_url",
            "bbb_recordings",

            # AI
            "ai_summary",
            "ai_flashcards",
            "ai_quiz",

            # Review
            "has_review",

            # Booking
            "booked_on_behalf",
            "booker_name",
            "booker_relationship",
            "booker_phone",
            "booker_email",

            "notes",

            # Computed
            "is_upcoming",
            "is_live",
            "bbb_available",
            "can_join",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "tutor_name",
            "student_name",
            "subject_name",

            "bbb_meeting_id",
            "bbb_tutor_join_url",
            "bbb_student_join_url",
            "bbb_status",
            "bbb_created_at",
            "bbb_started_at",
            "bbb_ended_at",

            "recording_available",
            "recording_url",
            "bbb_recordings",

            "ai_summary",
            "ai_flashcards",
            "ai_quiz",

            "has_review",

            "created_at",
            "updated_at",
        ]

    def get_is_upcoming(self, obj):
        return bool(
            obj.start_time
            and obj.start_time >= timezone.now()
            and obj.status not in {"cancelled", "completed", "no_show"}
        )

    def get_bbb_tutor_join_url(self, obj):
        return obj.bbb_join_url if obj.bbb_meeting_id else ""

    def get_bbb_student_join_url(self, obj):
        # Join URLs are generated per request so passwords are never stored.
        return "" if not obj.bbb_meeting_id else obj.bbb_join_url

    def get_bbb_status(self, obj):
        if not obj.bbb_meeting_id:
            return "not_created"
        if obj.status in {"completed", "cancelled", "no_show"}:
            return "ended"
        return "created"

    def get_bbb_created_at(self, obj):
        return obj.updated_at if obj.bbb_meeting_id else None

    def get_bbb_started_at(self, obj):
        return None

    def get_bbb_ended_at(self, obj):
        return obj.updated_at if obj.status == "completed" else None

    def get_bbb_recordings(self, obj):
        return []

    def get_bbb_available(self, obj):
        return bool(
            obj.bbb_meeting_id
            and obj.status not in {"completed", "cancelled", "no_show"}
        )

    def get_can_join(self, obj):
        if not obj.bbb_meeting_id:
            return False
        if obj.status in {"cancelled", "completed", "no_show"}:
            return False
        return timezone.now() >= obj.start_time - timedelta(minutes=10)

    def validate(self, attrs):

        start_time = attrs.get(
            "start_time",
            getattr(
                self.instance,
                "start_time",
                None,
            ),
        )

        end_time = attrs.get(
            "end_time",
            getattr(
                self.instance,
                "end_time",
                None,
            ),
        )

        if start_time and end_time:
            if end_time <= start_time:
                raise serializers.ValidationError(
                    {
                        "end_time": (
                            "End time must be after "
                            "start time."
                        )
                    }
                )

        return attrs


class LessonListSerializer(serializers.ModelSerializer):
    subject_name = serializers.ReadOnlyField()
    tutor_name = serializers.ReadOnlyField()
    student_name = serializers.ReadOnlyField()
    is_live = serializers.ReadOnlyField()
    bbb_status = serializers.SerializerMethodField()
    can_join = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            "id", "tutor", "student", "tutor_name", "student_name",
            "subject", "subject_name", "lesson_type", "status",
            "start_time", "end_time", "duration_minutes", "topic",
            "price", "currency", "payment_status", "bbb_status",
            "bbb_meeting_id", "recording_available", "is_live", "can_join",
            "created_at",
        ]

    def get_bbb_status(self, obj):
        if not obj.bbb_meeting_id:
            return "not_created"
        return "ended" if obj.status in {"completed", "cancelled", "no_show"} else "created"

    def get_can_join(self, obj):
        return bool(
            obj.bbb_meeting_id
            and obj.status not in {"completed", "cancelled", "no_show"}
            and timezone.now() >= obj.start_time - timedelta(minutes=10)
        )