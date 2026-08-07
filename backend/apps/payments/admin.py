from django.contrib import admin
from .models import Transaction, Payout, Dispute

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display  = ('id','payer','amount','payment_method','status','paystack_ref','created_at')
    list_filter   = ('status','payment_method')
    search_fields = ('payer__email','paystack_ref','description')
    raw_id_fields = ('payer','lesson')
    ordering      = ('-created_at',)

@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display  = ('id','tutor','amount','method','status','requested_at')
    list_filter   = ('status','method')
    raw_id_fields = ('tutor',)
    ordering      = ('-requested_at',)

@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display  = ('id','filed_by','status','amount','created_at')
    list_filter   = ('status',)
    raw_id_fields = ('filed_by','lesson')