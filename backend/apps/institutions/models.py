from django.db import models
from django.conf import settings

class Institution(models.Model):
    owner       = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='institution')
    name        = models.CharField(max_length=200)
    type        = models.CharField(max_length=50, default='school')
    description = models.TextField(blank=True)
    website     = models.URLField(blank=True)
    logo        = models.ImageField(upload_to='institutions/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

class InstitutionMember(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='members')
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='institution_memberships')
    role        = models.CharField(max_length=20, default='student')
    added_at    = models.DateTimeField(auto_now_add=True)
    class Meta: unique_together = ('institution','user')