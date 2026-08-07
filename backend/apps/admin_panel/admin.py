from django.contrib import admin
from .models import ModerationItem

@admin.register(ModerationItem)
class ModerationItemAdmin(admin.ModelAdmin):
    list_display  = ('content_type','author','flag_count','status','created_at')
    list_filter   = ('content_type','status')
    search_fields = ('content','author__email')
    raw_id_fields = ('author',)