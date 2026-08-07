from django.db import models
from django.conf import settings

class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, default='bi-book')
    class Meta: ordering = ['name']
    def __str__(self): return self.name

class TutorProfile(models.Model):
    APPROVAL = [('pending','Pending'),('approved','Approved'),('rejected','Rejected'),('suspended','Suspended')]
    STYLE    = [('interactive','Interactive'),('lecture','Lecture'),('socratic','Socratic'),('project','Project-based'),('visual','Visual')]

    user               = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tutor_profile')
    subjects           = models.ManyToManyField(Subject, blank=True, related_name='tutors')
    headline           = models.CharField(max_length=200, blank=True)
    bio                = models.TextField(blank=True)
    years_experience   = models.PositiveIntegerField(default=0)
    hourly_rate        = models.DecimalField(max_digits=8, decimal_places=2, default=60)
    teaching_style     = models.CharField(max_length=20, choices=STYLE, default='interactive')
    slug               = models.SlugField(unique=True, blank=True)
    approval_status    = models.CharField(max_length=20, choices=APPROVAL, default='pending')
    is_featured        = models.BooleanField(default=False)
    is_top_rated       = models.BooleanField(default=False)
    instant_book       = models.BooleanField(default=True)
    trial_lesson_enabled = models.BooleanField(default=False)
    trial_lesson_price = models.DecimalField(max_digits=8, decimal_places=2, default=30)
    intro_video_url    = models.URLField(blank=True)
    record_by_default  = models.BooleanField(default=True)
    average_rating     = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews      = models.PositiveIntegerField(default=0)
    total_lessons      = models.PositiveIntegerField(default=0)
    total_students     = models.PositiveIntegerField(default=0)
    response_time      = models.PositiveIntegerField(default=60)  # minutes
    total_earnings     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pending_payout     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_paid_out     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    education          = models.JSONField(default=list)
    certifications     = models.JSONField(default=list)
    availability       = models.JSONField(default=list)
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)

    class Meta: db_table = 'tutor_profiles'
    def __str__(self): return f'{self.user.get_full_name()} — {self.approval_status}'

class TutorFavourite(models.Model):
    student    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favourites')
    tutor      = models.ForeignKey(TutorProfile, on_delete=models.CASCADE, related_name='favourited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: unique_together = ('student','tutor')

class TutorDocument(models.Model):
    TYPES = [('id','Government ID'),('cert','Certificate'),('degree','Degree'),('other','Other')]
    tutor       = models.ForeignKey(TutorProfile, on_delete=models.CASCADE, related_name='documents')
    doc_type    = models.CharField(max_length=10, choices=TYPES)
    file        = models.FileField(upload_to='tutor_docs/')
    is_verified = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)