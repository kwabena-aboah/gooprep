from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('tutors', '0001_initial')]

    operations = [
        migrations.AddField(
            model_name='tutorprofile',
            name='blocked_dates',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='tutorprofile',
            name='packages',
            field=models.JSONField(default=list),
        ),
    ]
