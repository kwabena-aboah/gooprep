from django.db import models
from django.conf import settings

class StudentProfile(models.Model):
    user             = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    education_level  = models.CharField(max_length=50, blank=True)
    school           = models.CharField(max_length=200, blank=True)
    subjects_interest = models.JSONField(default=list)
    learning_goals   = models.TextField(blank=True)
    identity_document_type = models.CharField(max_length=30, blank=True)
    needs_approval   = models.BooleanField(default=True)
    is_approved      = models.BooleanField(default=False)
    approved_by      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_students')
    approved_at      = models.DateTimeField(blank=True, null=True)
    created_at       = models.DateTimeField(auto_now_add=True)