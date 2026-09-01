from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    ROLES = [('student','Student'),('tutor','Tutor'),('institution','Institution'),('admin','Admin')]
    PLANS = [('free','Free'),('pro','Pro'),('institution','Institution')]

    email        = models.EmailField(unique=True)
    role         = models.CharField(max_length=20, choices=ROLES, default='student')
    phone        = models.CharField(max_length=30, blank=True)
    bio          = models.TextField(blank=True)
    avatar       = models.ImageField(upload_to='avatars/', blank=True, null=True)
    avatar_url   = models.URLField(blank=True)
    city         = models.CharField(max_length=100, blank=True)
    address      = models.TextField(blank=True)
    country      = models.CharField(max_length=100, default='Ghana')
    date_of_birth = models.DateField(blank=True, null=True)
    gender       = models.CharField(max_length=30, blank=True)
    timezone     = models.CharField(max_length=50, default='Africa/Accra')
    language     = models.CharField(max_length=10, default='en')
    subscription_plan    = models.CharField(max_length=20, choices=PLANS, default='free')
    subscription_expires = models.DateTimeField(blank=True, null=True)
    total_points = models.IntegerField(default=0)
    level        = models.IntegerField(default=1)
    streak_days  = models.IntegerField(default=0)
    last_active  = models.DateField(blank=True, null=True)
    notify_email = models.BooleanField(default=True)
    notify_sms   = models.BooleanField(default=True)
    notify_push  = models.BooleanField(default=True)
    notify_whatsapp = models.BooleanField(default=False)
    guppy_user_id = models.CharField(max_length=200, blank=True)
    # Referral
    was_referred    = models.BooleanField(default=False)
    referrer_name   = models.CharField(max_length=200, blank=True)
    referrer_notes  = models.CharField(max_length=500, blank=True)
    email_verified  = models.BooleanField(default=False)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return self.avatar_url or f'https://ui-avatars.com/api/?name={self.get_full_name() or self.email}&background=e63900&color=fff'

class EmailVerificationToken(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_verification_tokens')
    token      = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used       = models.BooleanField(default=False)

    def is_valid(self):
        from datetime import timedelta
        return not self.used and (timezone.now() - self.created_at) < timedelta(hours=24)


class Notification(models.Model):
    TYPES = [
        ('lesson_booked','Lesson Booked'),('lesson_reminder','Lesson Reminder'),
        ('lesson_started','Lesson Started'),('lesson_completed','Lesson Completed'),
        ('lesson_cancelled','Lesson Cancelled'),('payment_received','Payment Received'),
        ('review_received','Review Received'),('message_received','Message Received'),
        ('tutor_approved','Tutor Approved'),('student_approved','Student Approved'),('system','System'),
    ]
    user              = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=TYPES, default='system')
    title   = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    link    = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'notifications'

class PasswordResetToken(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    token      = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used       = models.BooleanField(default=False)

    def is_valid(self):
        from datetime import timedelta
        return not self.used and (timezone.now() - self.created_at) < timedelta(hours=24)