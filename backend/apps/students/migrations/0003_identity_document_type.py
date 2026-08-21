from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('students', '0002_approval_defaults'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentprofile',
            name='identity_document_type',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
