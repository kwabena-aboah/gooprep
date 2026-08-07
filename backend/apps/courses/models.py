from django.db import models
from django.conf import settings

class GroupClass(models.Model):
    LEVELS = [('beginner','Beginner'),('intermediate','Intermediate'),('advanced','Advanced')]
    tutor            = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='group_classes')
    subject          = models.ForeignKey('tutors.Subject', on_delete=models.SET_NULL, null=True, blank=True)
    title            = models.CharField(max_length=200)
    description      = models.TextField()
    level            = models.CharField(max_length=20, choices=LEVELS, default='beginner')
    start_time       = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    max_students     = models.PositiveIntegerField(default=10)
    price            = models.DecimalField(max_digits=8, decimal_places=2)
    is_active        = models.BooleanField(default=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    @property
    def enrolled(self): return self.enrollments.count()
    @property
    def tutor_name(self): return self.tutor.get_full_name()
    @property
    def subject_name(self): return self.subject.name if self.subject else ''

class GroupClassEnrollment(models.Model):
    group_class = models.ForeignKey(GroupClass, on_delete=models.CASCADE, related_name='enrollments')
    student     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    class Meta: unique_together = ('group_class','student')