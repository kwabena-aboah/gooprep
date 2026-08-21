from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('tutors', '0004_booking_settings'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='tutorprofile',
            name='identity_document_type',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.CreateModel(
            name='UserDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doc_type', models.CharField(choices=[('ghana_passport_card', 'Ghana passport card'), ('voters_id_card', "Voter's ID card"), ('drivers_license', "Driver's license"), ('other_id', 'Other identity document'), ('professional_certificate', 'Professional certificate'), ('degree_certificate', 'Degree certificate'), ('other', 'Other document')], max_length=30)),
                ('file', models.FileField(upload_to='verification_documents/')),
                ('is_verified', models.BooleanField(default=False)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='verification_documents', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-uploaded_at']},
        ),
    ]
