from django.db import models
from django.conf import settings

class Transaction(models.Model):
    METHODS  = [('card','Card'),('mtn_momo','MTN MoMo'),('at_momo','AirtelTigo'),('tel_cash','Telecel Cash'),('bank','Bank Transfer')]
    STATUSES = [('pending','Pending'),('success','Success'),('failed','Failed'),('refunded','Refunded')]

    payer          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    lesson         = models.ForeignKey('scheduling.Lesson', on_delete=models.SET_NULL, null=True, blank=True)
    amount         = models.DecimalField(max_digits=10, decimal_places=2)
    currency       = models.CharField(max_length=3, default='GHS')
    payment_method = models.CharField(max_length=20, choices=METHODS, default='mtn_momo')
    status         = models.CharField(max_length=20, choices=STATUSES, default='pending')
    paystack_ref   = models.CharField(max_length=200, blank=True, unique=True, null=True)
    description    = models.CharField(max_length=300, blank=True)
    metadata       = models.JSONField(default=dict)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta: ordering = ['-created_at']

    @property
    def payer_name(self): return self.payer.get_full_name()

class Payout(models.Model):
    tutor        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payouts')
    amount       = models.DecimalField(max_digits=10, decimal_places=2)
    method       = models.CharField(max_length=20, default='mtn_momo')
    details      = models.JSONField(default=dict)
    status       = models.CharField(max_length=20, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)

class Dispute(models.Model):
    lesson     = models.ForeignKey('scheduling.Lesson', on_delete=models.CASCADE, related_name='disputes')
    filed_by   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason     = models.TextField()
    status     = models.CharField(max_length=20, default='open')
    resolution = models.TextField(blank=True)
    amount     = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)