import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def _recipient_addresses(lesson):
    """Return distinct, opted-in recipients for a paid lesson."""
    users = [lesson.student, lesson.tutor]
    if lesson.booked_on_behalf and lesson.booker_email:
        users.append(type("Booker", (), {"email": lesson.booker_email, "notify_email": True})())
    try:
        institution_ids = set(lesson.student.institution_memberships.values_list("institution_id", flat=True))
        if lesson.booked_on_behalf and lesson.booker_email:
            User = get_user_model()
            booker = User.objects.filter(email__iexact=lesson.booker_email).first()
            if booker:
                institution_ids.update(booker.institution_memberships.values_list("institution_id", flat=True))
        User = get_user_model()
        users.extend(
            User.objects.filter(
                institution__id__in=institution_ids,
                notify_email=True,
            )
        )
    except (AttributeError, TypeError):
        pass
    addresses = []
    for user in users:
        email = getattr(user, "email", "")
        if email and getattr(user, "notify_email", True) and email not in addresses:
            addresses.append(email)
    return addresses


def send_paid_lesson_receipt(transaction):
    """Send one receipt after payment succeeds; callers ensure idempotency."""
    lesson = transaction.lesson
    if not lesson:
        return
    subject_name = getattr(lesson, "subject_name", "Tutoring Session")
    date_text = lesson.start_time.astimezone().strftime("%A, %d %B %Y at %H:%M")
    body = (
        "Your Gooprep tutor booking is confirmed.\n\n"
        f"Student: {lesson.student.get_full_name() or lesson.student.email}\n"
        f"Tutor: {lesson.tutor.get_full_name() or lesson.tutor.email}\n"
        f"Subject: {subject_name}\n"
        f"Lesson: {date_text}\n"
        f"Duration: {lesson.duration_minutes} minutes\n"
        f"Amount paid: {transaction.currency} {transaction.amount:.2f}\n"
        f"Payment method: {transaction.get_payment_method_display()}\n"
        f"Payment reference: {transaction.paystack_ref}\n"
    )
    if lesson.booked_on_behalf:
        body += f"Booked on behalf of: {lesson.booker_name or lesson.booker_email}\n"
    send_mail(
        "Gooprep booking confirmed and payment receipt",
        body,
        settings.DEFAULT_FROM_EMAIL,
        _recipient_addresses(lesson),
        fail_silently=False,
    )
    logger.info("Paid lesson receipt sent for transaction %s", transaction.pk)
