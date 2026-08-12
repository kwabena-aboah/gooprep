from django.db import models
from django.conf import settings


class Lesson(models.Model):
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

    subject = models.ForeignKey(
        "tutors.Subject",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

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
        default=60
    )

    topic = models.CharField(
        max_length=300,
        blank=True,
    )

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

    bbb_meeting_id = models.CharField(
        max_length=200,
        blank=True,
    )

    bbb_join_url = models.URLField(
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

    ai_summary = models.TextField(
        blank=True,
    )

    ai_flashcards = models.JSONField(
        default=list,
    )

    ai_quiz = models.JSONField(
        default=list,
    )

    has_review = models.BooleanField(
        default=False,
    )

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

    notes = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-start_time"]
        db_table = "lessons"

    @property
    def subject_name(self):
        return (
            self.subject.name
            if self.subject
            else "Tutoring Session"
        )

    @property
    def tutor_name(self):
        return (
            self.tutor.get_full_name()
            or self.tutor.username
        )

    @property
    def student_name(self):
        return (
            self.student.get_full_name()
            or self.student.username
        )


class BBBWebhookEvent(models.Model):
    """Store raw BBB webhook events for audit / processing."""
    event_type  = models.CharField(max_length=100)
    meeting_id  = models.CharField(max_length=200)
    payload     = models.JSONField(default=dict)
    processed   = models.BooleanField(default=False)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bbb_webhook_events'
        ordering = ['-received_at']