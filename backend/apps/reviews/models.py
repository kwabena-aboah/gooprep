from django.db import models
from django.conf import settings

class Review(models.Model):
    lesson          = models.OneToOneField('scheduling.Lesson', on_delete=models.CASCADE, related_name='review')
    tutor           = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_reviews')
    reviewer        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_reviews')
    rating          = models.PositiveIntegerField()
    content         = models.TextField()
    communication_rating = models.PositiveIntegerField(blank=True, null=True)
    expertise_rating     = models.PositiveIntegerField(blank=True, null=True)
    punctuality_rating   = models.PositiveIntegerField(blank=True, null=True)
    would_recommend = models.BooleanField(default=True)
    tutor_response  = models.TextField(blank=True)
    is_approved     = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-created_at']