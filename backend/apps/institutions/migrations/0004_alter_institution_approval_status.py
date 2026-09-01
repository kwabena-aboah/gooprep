from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("institutions", "0003_approval_fields")]

    operations = [
        migrations.AlterField(
            model_name="institution",
            name="approval_status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("approved", "Approved"),
                    ("rejected", "Rejected"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
    ]
