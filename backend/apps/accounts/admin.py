from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Notification, PasswordResetToken

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ('email','get_full_name','role','subscription_plan','is_active','total_points','level','date_joined')
    list_filter   = ('role','subscription_plan','is_active','was_referred')
    search_fields = ('email','first_name','last_name','phone')
    ordering      = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('email','username','password')}),
        ('Personal', {'fields': ('first_name','last_name','phone','bio','avatar','avatar_url','city','country','date_of_birth')}),
        ('Platform', {'fields': ('role','subscription_plan','subscription_expires','timezone','language','guppy_user_id')}),
        ('Gamification', {'fields': ('total_points','level','streak_days','last_active')}),
        ('Notifications', {'fields': ('notify_email','notify_sms','notify_push','notify_whatsapp')}),
        ('Referral', {'fields': ('was_referred','referrer_name','referrer_notes')}),
        ('Permissions', {'fields': ('is_active','is_staff','is_superuser','groups','user_permissions')}),
    )
    add_fieldsets = ((None, {'classes':('wide',), 'fields':('email','username','password1','password2','role')}),)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ('user','notification_type','title','is_read','created_at')
    list_filter   = ('notification_type','is_read')
    search_fields = ('user__email','title')
    raw_id_fields = ('user',)

@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user','token','created_at','used')
    raw_id_fields = ('user',)