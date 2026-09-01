from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [("institutions", "0002_contact_fields")]

    operations = [
        migrations.AddField(
            model_name="institution", name="approval_status",
            field=models.CharField(default="pending", max_length=20),
        ),
        migrations.AddField(
            model_name="institution", name="rejection_reason",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="institution", name="reviewed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="institution", name="reviewed_by",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="reviewed_institutions", to=settings.AUTH_USER_MODEL),
        ),
    ]
