from django.db import migrations


def create_default_badges(apps, schema_editor):
    Badge = apps.get_model('gamification', 'Badge')
    defaults = [
        ('First Steps', 'bi bi-flag-fill', '#3b82f6', 'Complete your first learning activity.', 10),
        ('Lesson Learner', 'bi bi-book-fill', '#10b981', 'Complete a lesson.', 100),
        ('Point Starter', 'bi bi-star-fill', '#f59e0b', 'Earn 250 points.', 250),
        ('Scholar', 'bi bi-mortarboard-fill', '#8b5cf6', 'Earn 500 points.', 500),
        ('Point Master', 'bi bi-trophy-fill', '#e63900', 'Earn 1000 points.', 1000),
    ]
    for name, icon, color, description, points_required in defaults:
        Badge.objects.get_or_create(
            name=name,
            defaults={
                'icon': icon,
                'color': color,
                'description': description,
                'points_required': points_required,
            },
        )


def remove_default_badges(apps, schema_editor):
    Badge = apps.get_model('gamification', 'Badge')
    Badge.objects.filter(name__in=[
        'First Steps', 'Lesson Learner', 'Point Starter', 'Scholar', 'Point Master',
    ]).delete()


class Migration(migrations.Migration):
    dependencies = [('gamification', '0001_initial')]
    operations = [migrations.RunPython(create_default_badges, remove_default_badges)]
