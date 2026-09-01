from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("scheduling", "0002_bbbwebhookevent"),
    ]

    operations = [
        migrations.AddField(
            model_name="lesson",
            name="bbb_status",
            field=models.CharField(default="not_created", max_length=20),
        ),
        migrations.AddField(
            model_name="lesson",
            name="bbb_created_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="lesson",
            name="bbb_started_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="lesson",
            name="bbb_ended_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="lesson",
            name="bbb_recordings",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
