from django.db import models
from django.conf import settings

class Conversation(models.Model):
    participants    = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    created_at      = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(auto_now_add=True)
    last_message    = models.CharField(max_length=500, blank=True)
    guppy_conv_id   = models.CharField(max_length=200, blank=True, db_index=True)
    class Meta: ordering = ['-last_message_at']

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content      = models.TextField()
    is_read      = models.BooleanField(default=False)
    attachment   = models.FileField(upload_to='chat_attachments/', blank=True, null=True)
    guppy_msg_id = models.CharField(max_length=200, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['created_at']