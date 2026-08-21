from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('tutors', '0003_tutorprofile_blocked_dates_packages')]

    operations = [
        migrations.AddField(
            model_name='tutorprofile', name='min_notice_hours',
            field=models.PositiveIntegerField(default=24),
        ),
        migrations.AddField(
            model_name='tutorprofile', name='max_daily_bookings',
            field=models.PositiveIntegerField(default=6),
        ),
        migrations.AddField(
            model_name='tutorprofile', name='booking_buffer_minutes',
            field=models.PositiveIntegerField(default=15),
        ),
    ]
