from django.contrib import admin
from .models import Conversation, Message

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id','last_message','last_message_at','guppy_conv_id')
    search_fields = ('guppy_conv_id','participants__email')
    filter_horizontal = ('participants',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display  = ('id','conversation','sender','is_read','created_at')
    raw_id_fields = ('conversation','sender')
    ordering      = ('-created_at',)