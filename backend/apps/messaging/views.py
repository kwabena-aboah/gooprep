import json
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from .serializers import MessageSerializer
from .guppy import get_or_create_guppy_user, create_conversation as guppy_create_conv, verify_webhook, get_guppy_status, register_user

User = get_user_model()

def _ser_conv(conv, request_user):
    other = conv.participants.exclude(id=request_user.id).first()
    unread = conv.messages.filter(is_read=False).exclude(sender=request_user).count()
    return {
        'id': conv.id,
        'other_user': {'id':other.id,'name':other.get_full_name(),'avatar':other.get_avatar_url()} if other else None,
        'last_message': conv.last_message,
        'last_message_at': conv.last_message_at.isoformat() if conv.last_message_at else None,
        'unread_count': unread,
        'guppy_conv_id': conv.guppy_conv_id,
    }

class ConversationListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        convs = Conversation.objects.filter(participants=request.user).prefetch_related('participants','messages')
        return Response({'count':convs.count(),'results':[_ser_conv(c,request.user) for c in convs]})
    def post(self, request):
        other_id = request.data.get('user_id')
        try: other = User.objects.get(id=other_id)
        except: return Response({'error':'User not found.'}, status=404)
        conv = Conversation.objects.filter(participants=request.user).filter(participants=other).first()
        if not conv:
            conv = Conversation.objects.create()
            conv.participants.add(request.user, other)
            try:
                my_gid    = get_or_create_guppy_user(request.user)
                other_gid = get_or_create_guppy_user(other)
                if my_gid and other_gid:
                    gc = guppy_create_conv([my_gid, other_gid], {'gooprep_conv_id':conv.id})
                    if gc: conv.guppy_conv_id = gc.get('id',''); conv.save(update_fields=['guppy_conv_id'])
            except Exception: pass
        return Response({'id':conv.id})

class MessageListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, conv_id):
        try: conv = Conversation.objects.filter(participants=request.user).get(id=conv_id)
        except: return Response({'error':'Not found.'}, status=404)
        conv.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
        msgs = conv.messages.select_related('sender').all()
        return Response({'results': MessageSerializer(msgs, many=True).data})
    def post(self, request, conv_id):
        try: conv = Conversation.objects.filter(participants=request.user).get(id=conv_id)
        except: return Response({'error':'Not found.'}, status=404)
        content = request.data.get('content','').strip()
        if not content: return Response({'error':'Content required.'}, status=400)
        msg = Message.objects.create(conversation=conv, sender=request.user, content=content)
        conv.last_message    = content[:200]
        conv.last_message_at = timezone.now()
        conv.save(update_fields=['last_message','last_message_at'])
        # Notify other participants
        for participant in conv.participants.exclude(id=request.user.id):
            from apps.accounts.models import Notification
            Notification.objects.create(user=participant, notification_type='message_received',
                title=f'New message from {request.user.get_full_name()}', message=content[:100], link='/messages')
        return Response(MessageSerializer(msg).data, status=201)

class GuppyWebhookView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        sig = request.headers.get('X-Guppy-Signature', '') or request.headers.get('X-GUPPY-SIGNATURE', '')
        if not verify_webhook(request.body, sig):
            return Response({'error':'Invalid signature.'}, status=403)
        try:
            event = json.loads(request.body)
            event_type = event.get('type')
            data       = event.get('data', {})
            if event_type == 'message.received':
                self._handle_message(data)
        except (TypeError, ValueError, json.JSONDecodeError):
            return Response({'error': 'Invalid JSON.'}, status=400)
        return Response({'received': True})

    def _handle_message(self, data):
        try:
            guppy_conv_id = data.get('conversation_id')
            conv = Conversation.objects.filter(guppy_conv_id=guppy_conv_id).first()
            if not conv: return
            sender_ext = data.get('sender',{}).get('external_id')
            sender = User.objects.filter(id=sender_ext).first()
            if not sender: return
            content = data.get('content','')
            msg = Message.objects.create(conversation=conv, sender=sender, content=content)
            conv.last_message=content[:200]; conv.last_message_at=timezone.now()
            conv.save(update_fields=['last_message','last_message_at'])
            for p in conv.participants.exclude(id=sender.id):
                from apps.accounts.models import Notification
                Notification.objects.create(user=p,notification_type='message_received',
                    title=f'New message from {sender.get_full_name()}',message=content[:100],link='/messages')
        except Exception as e:
            import logging; logging.getLogger(__name__).error(f'[Guppy] _handle_message: {e}')

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def guppy_status(request):
    return Response(get_guppy_status())

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def sync_guppy_user(request):
    gid = register_user(request.user)
    return Response({'guppy_user_id':gid,'synced':bool(gid)})