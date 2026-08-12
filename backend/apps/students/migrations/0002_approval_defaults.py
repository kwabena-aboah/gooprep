from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentprofile',
            name='needs_approval',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='studentprofile',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
    ]
