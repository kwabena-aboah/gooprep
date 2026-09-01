from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("institutions", "0001_initial")]

    operations = [
        migrations.AddField(model_name="institution", name="country", field=models.CharField(default="Ghana", max_length=100)),
        migrations.AddField(model_name="institution", name="city", field=models.CharField(blank=True, max_length=100)),
        migrations.AddField(model_name="institution", name="address", field=models.TextField(blank=True)),
        migrations.AddField(model_name="institution", name="contact_email", field=models.EmailField(blank=True, max_length=254)),
        migrations.AddField(model_name="institution", name="contact_phone", field=models.CharField(blank=True, max_length=30)),
        migrations.AddField(model_name="institution", name="is_active", field=models.BooleanField(default=True)),
    ]
