from django.db import migrations


LESSON_POINTS = 100


def backfill_completed_lessons(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    Lesson = apps.get_model('scheduling', 'Lesson')
    PointsHistory = apps.get_model('gamification', 'PointsHistory')
    Badge = apps.get_model('gamification', 'Badge')
    UserBadge = apps.get_model('gamification', 'UserBadge')

    for lesson in Lesson.objects.filter(status='completed').only('id', 'student_id'):
        action = f'lesson_completed:{lesson.id}'
        if PointsHistory.objects.filter(user_id=lesson.student_id, action=action).exists():
            continue
        PointsHistory.objects.create(
            user_id=lesson.student_id,
            points=LESSON_POINTS,
            action=action,
            description=f'Completed lesson #{lesson.id}',
        )
        user = User.objects.get(pk=lesson.student_id)
        user.total_points += LESSON_POINTS
        user.level = max(1, user.total_points // 500 + 1)
        user.save(update_fields=['total_points', 'level'])

    for user in User.objects.all().only('id', 'total_points'):
        for badge in Badge.objects.filter(points_required__lte=user.total_points):
            UserBadge.objects.get_or_create(user_id=user.id, badge_id=badge.id)


def reverse_backfill(apps, schema_editor):
    PointsHistory = apps.get_model('gamification', 'PointsHistory')
    User = apps.get_model('accounts', 'User')
    Lesson = apps.get_model('scheduling', 'Lesson')

    for lesson in Lesson.objects.filter(status='completed').only('id', 'student_id'):
        deleted, _ = PointsHistory.objects.filter(
            user_id=lesson.student_id,
            action=f'lesson_completed:{lesson.id}',
        ).delete()
        if deleted:
            user = User.objects.get(pk=lesson.student_id)
            user.total_points = max(0, user.total_points - LESSON_POINTS)
            user.level = max(1, user.total_points // 500 + 1)
            user.save(update_fields=['total_points', 'level'])


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),
        ('scheduling', '0002_bbbwebhookevent'),
        ('gamification', '0002_default_badges'),
    ]
    operations = [
        migrations.RunPython(backfill_completed_lessons, reverse_backfill),
    ]
