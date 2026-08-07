from django.contrib import admin
from .models import Badge, UserBadge, PointsHistory, LeaderboardEntry

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display  = ('name','icon','color','points_required')
    search_fields = ('name',)

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display  = ('user','badge','earned_at')
    raw_id_fields = ('user',)

@admin.register(PointsHistory)
class PointsHistoryAdmin(admin.ModelAdmin):
    list_display  = ('user','points','action','created_at')
    raw_id_fields = ('user',)
    ordering      = ('-created_at',)

@admin.register(LeaderboardEntry)
class LeaderboardEntryAdmin(admin.ModelAdmin):
    list_display = ('user','role','rank','points','week')