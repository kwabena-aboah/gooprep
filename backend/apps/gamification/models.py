from django.db import models
from django.conf import settings

class Badge(models.Model):
    name             = models.CharField(max_length=100, unique=True)
    icon             = models.CharField(max_length=50, default='bi bi-award-fill')
    color            = models.CharField(max_length=20, default='#e63900')
    description      = models.TextField(blank=True)
    points_required  = models.IntegerField(default=0)
    def __str__(self): return self.name

class UserBadge(models.Model):
    user      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='badges')
    badge     = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    class Meta: unique_together = ('user','badge')

class PointsHistory(models.Model):
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='points_history')
    points      = models.IntegerField()
    action      = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-created_at']

class LeaderboardEntry(models.Model):
    user   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role   = models.CharField(max_length=20, default='student')
    rank   = models.IntegerField()
    points = models.IntegerField()
    week   = models.DateField()
    class Meta: unique_together = ('user','week')