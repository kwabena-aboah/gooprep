from django.db import migrations, models


def populate_event_ids(apps, schema_editor):
    event_model = apps.get_model("scheduling", "BBBWebhookEvent")
    for event in event_model.objects.filter(event_id__isnull=True):
        event.event_id = f"legacy-{event.pk}"
        event.save(update_fields=["event_id"])


class Migration(migrations.Migration):
    dependencies = [("scheduling", "0003_bbb_fields")]

    operations = [
        migrations.AddField(
            model_name="bbbwebhookevent",
            name="event_id",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name="bbbwebhookevent",
            name="record_id",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name="bbbwebhookevent",
            name="processed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="bbbwebhookevent",
            name="processing_error",
            field=models.TextField(blank=True),
        ),
        migrations.RunPython(populate_event_ids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="bbbwebhookevent",
            name="event_id",
            field=models.CharField(db_index=True, max_length=200, unique=True),
        ),
    ]
