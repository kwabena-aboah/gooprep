from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import Badge, PointsHistory, UserBadge


DAILY_ACTIVITY_POINTS = 10
COMPLETED_LESSON_POINTS = 100


@transaction.atomic
def award_points(user, points, action, description=''):
    """Award points once for a concrete activity and refresh badges."""
    user = type(user).objects.select_for_update().get(pk=user.pk)
    user.total_points += int(points)
    user.level = max(1, user.total_points // 500 + 1)
    user.save(update_fields=['total_points', 'level'])
    history = PointsHistory.objects.create(
        user=user,
        points=int(points),
        action=action,
        description=description,
    )
    check_badges(user)
    return user, history


def check_badges(user):
    for badge in Badge.objects.all():
        if user.total_points >= badge.points_required:
            UserBadge.objects.get_or_create(user=user, badge=badge)


@transaction.atomic
def record_daily_activity(user):
    """Record today's activity and award one daily streak bonus."""
    today = timezone.localdate()
    user = type(user).objects.select_for_update().get(pk=user.pk)
    if user.last_active == today:
        return user, False

    yesterday = today - timedelta(days=1)
    user.streak_days = user.streak_days + 1 if user.last_active == yesterday else 1
    user.last_active = today
    user.save(update_fields=['streak_days', 'last_active'])
    user, _ = award_points(
        user,
        DAILY_ACTIVITY_POINTS,
        'daily_activity',
        f'Daily activity streak: {user.streak_days} day(s)',
    )
    return user, True


def record_completed_lesson(lesson):
    """Award completion points once and count the lesson as daily activity."""
    record_daily_activity(lesson.student)
    action = f'lesson_completed:{lesson.pk}'
    if PointsHistory.objects.filter(user=lesson.student, action=action).exists():
        return lesson.student, False
    return award_points(
        lesson.student,
        COMPLETED_LESSON_POINTS,
        action,
        f'Completed lesson #{lesson.pk}',
    )[0], True

