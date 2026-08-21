from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('settings_app', '0001_initial')]

    operations = [
        migrations.AlterField(
            model_name='sitesettings',
            name='commission_rate',
            field=models.DecimalField(decimal_places=2, default=20, max_digits=4),
        ),
    ]
