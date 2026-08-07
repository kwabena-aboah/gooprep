from django.contrib import admin
from .models import AIConversation, StudentProgress

@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    list_display  = ('user','created_at','updated_at')
    raw_id_fields = ('user',)

@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display  = ('student','subject','score_before','score_after','lessons_completed','last_updated')
    raw_id_fields = ('student','subject')