from rest_framework import serializers
from .models import Badge, UserBadge, PointsHistory

class BadgeSerializer(serializers.ModelSerializer):
    class Meta: model = Badge; fields = ['id','name','icon','color','description','points_required']

class UserBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)
    class Meta: model = UserBadge; fields = ['id','badge','earned_at']

class PointsHistorySerializer(serializers.ModelSerializer):
    class Meta: model = PointsHistory; fields = ['id','points','action','description','created_at']