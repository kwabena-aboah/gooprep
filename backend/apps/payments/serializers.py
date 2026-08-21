from rest_framework import serializers
from .models import Transaction, Subscription, Payout, Dispute

class TransactionSerializer(serializers.ModelSerializer):
    payer_name = serializers.SerializerMethodField()
    lesson_subject = serializers.SerializerMethodField()
    lesson_duration = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ['id','payer_name','amount','currency','payment_method','status',
                  'paystack_ref','description','lesson_subject','lesson_duration','created_at']

    def get_payer_name(self, obj):
        return obj.payer.get_full_name()

    def get_lesson_subject(self, obj):
        return obj.lesson.subject.name if obj.lesson and obj.lesson.subject else ''

    def get_lesson_duration(self, obj):
        return obj.lesson.duration_minutes if obj.lesson else None

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'plan', 'billing_cycle', 'amount', 'status', 'paystack_ref', 'starts_at', 'expires_at', 'created_at']


class PayoutSerializer(serializers.ModelSerializer):
    class Meta: model = Payout; fields = ['id','amount','method','status','requested_at','processed_at']

class DisputeSerializer(serializers.ModelSerializer):
    filed_by_name = serializers.SerializerMethodField()
    class Meta:
        model = Dispute
        fields = ['id','filed_by_name','reason','status','resolution','amount','created_at']
    def get_filed_by_name(self, obj): return obj.filed_by.get_full_name()