from django.db import models
from django.conf import settings

class AIConversation(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_conversations')
    messages   = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class StudentProgress(models.Model):
    student    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress')
    subject    = models.ForeignKey('tutors.Subject', on_delete=models.CASCADE)
    score_before = models.FloatField(default=0)
    score_after  = models.FloatField(default=0)
    lessons_completed = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    class Meta: unique_together = ('student','subject')