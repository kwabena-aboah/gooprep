import os
from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from django.core.asgi import get_asgi_application
from channels.db import database_sync_to_async
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django_asgi_app = get_asgi_application()
from channels.generic.websocket import AsyncJsonWebsocketConsumer


@database_sync_to_async
def user_from_token(token):
    try:
        validated = UntypedToken(token)
        from django.contrib.auth import get_user_model
        return get_user_model().objects.get(id=validated['user_id'])
    except Exception:
        return AnonymousUser()


class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query = parse_qs(scope.get('query_string', b'').decode())
        token = query.get('token', [None])[0]
        scope['user'] = await user_from_token(token) if token else AnonymousUser()
        return await self.app(scope, receive, send)


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user')
        if not user or user.is_anonymous:
            await self.close(code=4401)
            return
        self.group = f'user_{user.id}'
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, 'group'):
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def notification(self, event):
        await self.send_json({'type': 'notification', 'data': event['data']})


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user')
        if not user or user.is_anonymous:
            await self.close(code=4401)
            return
        self.conv_id = self.scope['url_route']['kwargs']['conv_id']
        self.group = f'chat_{self.conv_id}'
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, 'group'):
            await self.channel_layer.group_discard(self.group, self.channel_name)

    @database_sync_to_async
    def save_message(self, content):
        from apps.messaging.models import Conversation, Message
        conversation = Conversation.objects.filter(
            id=self.conv_id, participants=self.scope['user']
        ).first()
        if not conversation:
            return None
        message = Message.objects.create(
            conversation=conversation, sender=self.scope['user'], content=content
        )
        from django.utils import timezone
        conversation.last_message = content[:200]
        conversation.last_message_at = timezone.now()
        conversation.save(update_fields=['last_message', 'last_message_at'])
        return {'id': message.id, 'content': message.content,
                'sender': self.scope['user'].id,
                'created_at': message.created_at.isoformat()}

    async def receive_json(self, content):
        event_type = content.get('type', 'message')
        if event_type == 'typing':
            await self.channel_layer.group_send(self.group, {
                'type': 'chat_event', 'event_type': 'typing',
                'data': {'user_id': self.scope['user'].id,
                         'is_typing': bool(content.get('is_typing'))},
            })
            return
        message = str(content.get('content', content.get('message', ''))).strip()
        if not message:
            return
        saved = await self.save_message(message)
        if saved:
            await self.channel_layer.group_send(self.group, {
                'type': 'chat_event', 'event_type': 'message', 'data': saved,
            })

    async def chat_event(self, event):
        await self.send_json({'type': event['event_type'], 'data': event['data']})


ws_urlpatterns = [
    re_path(r'^ws/notifications/$', NotificationConsumer.as_asgi()),
    re_path(r'^ws/chat/(?P<conv_id>\d+)/$', ChatConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': JWTAuthMiddleware(URLRouter(ws_urlpatterns)),
})
