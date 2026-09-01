from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("accounts", "0002_email_verification")]

    operations = [
        migrations.AddField(
            model_name="user",
            name="address",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="user",
            name="gender",
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
