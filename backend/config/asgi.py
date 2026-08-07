import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_asgi_app = get_asgi_application()

from channels.generic.websocket import AsyncJsonWebsocketConsumer

class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(f'user_{self.scope["user"].id}', self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(f'user_{self.scope["user"].id}', self.channel_name)

    async def notification(self, event):
        await self.send_json({'type': 'notification', 'data': event['data']})

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.conv_id = self.scope['url_route']['kwargs']['conv_id']
        self.group   = f'chat_{self.conv_id}'
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive_json(self, content):
        await self.channel_layer.group_send(self.group, {
            'type':    'chat_message',
            'message': content.get('message',''),
            'sender':  self.scope['user'].get_full_name(),
            'sender_id': self.scope['user'].id,
        })

    async def chat_message(self, event):
        await self.send_json(event)

ws_urlpatterns = [
    re_path(r'^ws/notifications/$',         NotificationConsumer.as_asgi()),
    re_path(r'^ws/chat/(?P<conv_id>\d+)/$', ChatConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(URLRouter(ws_urlpatterns)),
})