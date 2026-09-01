from django.conf import settings
from django.db import models


class Lesson(models.Model):

    # ==============================================================
    # Choices
    # ==============================================================

    TYPES = [
        ("regular", "Regular"),
        ("trial", "Trial"),
        ("group", "Group"),
    ]

    STATUSES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("no_show", "No Show"),
        ("rescheduled", "Rescheduled"),
    ]

    PAY_STATUS = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("refunded", "Refunded"),
        ("disputed", "Disputed"),
    ]

    # ==============================================================
    # Users
    # ==============================================================

    tutor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tutor_lessons",
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_lessons",
    )

    # ==============================================================
    # Subject
    # ==============================================================

    subject = models.ForeignKey(
        "tutors.Subject",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lessons",
    )

    # ==============================================================
    # Lesson information
    # ==============================================================

    lesson_type = models.CharField(
        max_length=20,
        choices=TYPES,
        default="regular",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUSES,
        default="pending",
    )

    start_time = models.DateTimeField()

    end_time = models.DateTimeField()

    duration_minutes = models.PositiveIntegerField(
        default=60,
    )

    topic = models.CharField(
        max_length=300,
        blank=True,
    )

    # ==============================================================
    # Payment
    # ==============================================================

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
    )

    currency = models.CharField(
        max_length=3,
        default="GHS",
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAY_STATUS,
        default="pending",
    )

    # ==============================================================
    # BigBlueButton
    # ==============================================================

    bbb_meeting_id = models.CharField(
        max_length=200,
        blank=True,
        db_index=True,
    )

    bbb_join_url = models.URLField(
        blank=True,
    )

    bbb_status = models.CharField(
        max_length=20,
        default="not_created",
    )

    bbb_created_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    bbb_started_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    bbb_ended_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    bbb_recordings = models.JSONField(
        default=list,
        blank=True,
    )

    record_session = models.BooleanField(
        default=True,
    )

    recording_available = models.BooleanField(
        default=False,
    )

    recording_url = models.URLField(
        blank=True,
    )

    # ==============================================================
    # AI-generated lesson information
    # ==============================================================

    ai_summary = models.TextField(
        blank=True,
    )

    ai_flashcards = models.JSONField(
        default=list,
        blank=True,
    )

    ai_quiz = models.JSONField(
        default=list,
        blank=True,
    )

    # ==============================================================
    # Review
    # ==============================================================

    has_review = models.BooleanField(
        default=False,
    )

    # ==============================================================
    # Booking on behalf of another person
    # ==============================================================

    booked_on_behalf = models.BooleanField(
        default=False,
    )

    booker_name = models.CharField(
        max_length=200,
        blank=True,
    )

    booker_relationship = models.CharField(
        max_length=50,
        blank=True,
    )

    booker_phone = models.CharField(
        max_length=30,
        blank=True,
    )

    booker_email = models.EmailField(
        blank=True,
    )

    # ==============================================================
    # Notes
    # ==============================================================

    notes = models.TextField(
        blank=True,
    )

    # ==============================================================
    # Timestamps
    # ==============================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    # ==============================================================
    # Meta
    # ==============================================================

    class Meta:
        db_table = "lessons"

        ordering = [
            "-start_time",
        ]

        indexes = [
            models.Index(
                fields=[
                    "tutor",
                    "start_time",
                ]
            ),
            models.Index(
                fields=[
                    "student",
                    "start_time",
                ]
            ),
            models.Index(
                fields=[
                    "status",
                    "start_time",
                ]
            ),
            models.Index(
                fields=[
                    "bbb_meeting_id",
                ]
            ),
            models.Index(
                fields=[
                    "payment_status",
                ]
            ),
        ]

    # ==============================================================
    # Properties
    # ==============================================================

    @property
    def subject_name(self):
        """
        Return the subject name without raising an error when
        the subject has been deleted.
        """

        if self.subject_id and self.subject:
            return self.subject.name

        return "Tutoring Session"

    @property
    def tutor_name(self):
        """
        Return the tutor's display name.
        """

        return (
            self.tutor.get_full_name()
            or getattr(
                self.tutor,
                "username",
                None,
            )
            or getattr(
                self.tutor,
                "email",
                "Tutor",
            )
        )

    @property
    def student_name(self):
        """
        Return the student's display name.
        """

        return (
            self.student.get_full_name()
            or getattr(
                self.student,
                "username",
                None,
            )
            or getattr(
                self.student,
                "email",
                "Student",
            )
        )

    @property
    def has_bbb_room(self):
        """
        Return True when this lesson has a BBB meeting.
        """

        return bool(
            self.bbb_meeting_id
        )

    @property
    def is_live(self):
        """
        Return True when the lesson is marked as in progress.
        """

        return self.status == "in_progress"


class BBBWebhookEvent(models.Model):
    """
    Stores raw BigBlueButton webhook events.

    This provides an audit trail and allows webhook processing
    to be retried without requiring BBB to send the event again.
    """

    event_id = models.CharField(
        max_length=200,
        unique=True,
        db_index=True,
    )

    event_type = models.CharField(
        max_length=100,
        db_index=True,
    )

    meeting_id = models.CharField(
        max_length=200,
        db_index=True,
    )

    record_id = models.CharField(
        max_length=200,
        blank=True,
    )

    payload = models.JSONField(
        default=dict,
    )

    processed = models.BooleanField(
        default=False,
        db_index=True,
    )

    received_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )

    processed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    processing_error = models.TextField(
        blank=True,
    )

    class Meta:
        db_table = "bbb_webhook_events"

        ordering = [
            "-received_at",
        ]

        indexes = [
            models.Index(
                fields=[
                    "meeting_id",
                    "event_type",
                ]
            ),
            models.Index(
                fields=[
                    "processed",
                    "received_at",
                ]
            ),
        ]

    def __str__(self):
        return (
            f"{self.event_type} - "
            f"{self.meeting_id}"
        )