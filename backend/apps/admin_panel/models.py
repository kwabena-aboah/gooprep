from django.db import models
from django.conf import settings

class ModerationItem(models.Model):
    TYPES = [('review','Review'),('message','Message'),('profile','Profile'),('other','Other')]
    content_type = models.CharField(max_length=20, choices=TYPES)
    content_id   = models.PositiveIntegerField()
    content      = models.TextField()
    author       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    reasons      = models.JSONField(default=list)
    flag_count   = models.PositiveIntegerField(default=1)
    status       = models.CharField(max_length=20, default='pending')
    resolution   = models.CharField(max_length=50, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    @property
    def author_name(self): return self.author.get_full_name() if self.author else 'Unknown'