from rest_framework import serializers
from .models import Conversation, Message

class MessageSerializer(serializers.ModelSerializer):
    sender_name   = serializers.SerializerMethodField()
    sender_avatar = serializers.SerializerMethodField()
    class Meta:
        model = Message
        fields = ['id','conversation','sender','sender_name','sender_avatar','content','is_read','created_at']
    def get_sender_name(self, obj):   return obj.sender.get_full_name()
    def get_sender_avatar(self, obj): return obj.sender.get_avatar_url()

class ConversationSerializer(serializers.ModelSerializer):
    class Meta: model = Conversation; fields = ['id','last_message','last_message_at','guppy_conv_id']