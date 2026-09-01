import os
from urllib.parse import parse_qs

# ---------------------------------------------------------------------------
# Django setup
# ---------------------------------------------------------------------------

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.asgi import get_asgi_application

# IMPORTANT:
# Initialize Django before importing anything that depends on Django's
# application registry, models, authentication, etc.
django_asgi_app = get_asgi_application()


# ---------------------------------------------------------------------------
# Channels imports
# ---------------------------------------------------------------------------

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.routing import ProtocolTypeRouter, URLRouter

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.urls import re_path

from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken


# ---------------------------------------------------------------------------
# JWT authentication
# ---------------------------------------------------------------------------

@database_sync_to_async
def user_from_token(token):
    """
    Validate a JWT and return the corresponding Django user.

    Returns AnonymousUser when:
    - token is missing/invalid
    - token is expired
    - user does not exist
    - token cannot be decoded
    """

    if not token:
        return AnonymousUser()

    try:
        validated_token = UntypedToken(token)

        user_id = validated_token.get("user_id")

        if not user_id:
            return AnonymousUser()

        User = get_user_model()

        return User.objects.get(id=user_id)

    except (
        InvalidToken,
        TokenError,
        User.DoesNotExist,
        KeyError,
        TypeError,
        ValueError,
    ):
        return AnonymousUser()

    except Exception:
        # Never allow authentication errors to crash the WebSocket worker.
        return AnonymousUser()


# ---------------------------------------------------------------------------
# JWT WebSocket middleware
# ---------------------------------------------------------------------------

class JWTAuthMiddleware:
    """
    Authenticate WebSocket connections using:

        /ws/.../?token=<JWT>

    The authenticated user is stored in:

        scope["user"]
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"")

        try:
            query_params = parse_qs(
                query_string.decode("utf-8")
            )
        except (UnicodeDecodeError, AttributeError):
            query_params = {}

        token = query_params.get("token", [None])[0]

        if token:
            scope["user"] = await user_from_token(token)
        else:
            scope["user"] = AnonymousUser()

        return await self.app(
            scope,
            receive,
            send,
        )


# ---------------------------------------------------------------------------
# Notification WebSocket consumer
# ---------------------------------------------------------------------------

class NotificationConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        user = self.scope.get("user")

        if not user or user.is_anonymous:
            await self.close(code=4401)
            return

        self.group = f"user_{user.id}"

        await self.channel_layer.group_add(
            self.group,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, code):
        group = getattr(self, "group", None)

        if group:
            await self.channel_layer.group_discard(
                group,
                self.channel_name,
            )

    async def notification(self, event):
        await self.send_json({
            "type": "notification",
            "data": event.get("data"),
        })


# ---------------------------------------------------------------------------
# Chat WebSocket consumer
# ---------------------------------------------------------------------------

class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        user = self.scope.get("user")

        if not user or user.is_anonymous:
            await self.close(code=4401)
            return

        try:
            self.conv_id = self.scope["url_route"]["kwargs"]["conv_id"]
        except (KeyError, TypeError):
            await self.close(code=4400)
            return

        self.group = f"chat_{self.conv_id}"

        await self.channel_layer.group_add(
            self.group,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, code):
        group = getattr(self, "group", None)

        if group:
            await self.channel_layer.group_discard(
                group,
                self.channel_name,
            )

    @database_sync_to_async
    def save_message(self, content):
        """
        Save a chat message after verifying that the authenticated user
        belongs to the conversation.
        """

        from apps.messaging.models import Conversation, Message
        from django.utils import timezone

        user = self.scope.get("user")

        if not user or user.is_anonymous:
            return None

        conversation = (
            Conversation.objects
            .filter(
                id=self.conv_id,
                participants=user,
            )
            .first()
        )

        if not conversation:
            return None

        message = Message.objects.create(
            conversation=conversation,
            sender=user,
            content=content,
        )

        # ---------------------------------------------------------------
        # Guppy integration
        # ---------------------------------------------------------------

        if conversation.guppy_conv_id:

            try:
                from apps.messaging.guppy import (
                    get_or_create_guppy_user,
                    send_message,
                )

                sender_gid = get_or_create_guppy_user(user)

                if sender_gid:

                    remote = send_message(
                        conversation.guppy_conv_id,
                        sender_gid,
                        content,
                    )

                    if remote and remote.get("id"):
                        message.guppy_msg_id = str(
                            remote["id"]
                        )

                        message.save(
                            update_fields=["guppy_msg_id"]
                        )

            except Exception:
                # Do not prevent the local message from being saved if
                # Guppy is temporarily unavailable.
                pass

        # ---------------------------------------------------------------
        # Update conversation
        # ---------------------------------------------------------------

        conversation.last_message = content[:200]
        conversation.last_message_at = timezone.now()

        conversation.save(
            update_fields=[
                "last_message",
                "last_message_at",
            ]
        )

        return {
            "id": message.id,
            "content": message.content,
            "sender": user.id,
            "created_at": message.created_at.isoformat(),
        }

    async def receive_json(self, content, **kwargs):

        if not isinstance(content, dict):
            return

        event_type = content.get("type", "message")

        # ---------------------------------------------------------------
        # Typing indicator
        # ---------------------------------------------------------------

        if event_type == "typing":

            await self.channel_layer.group_send(
                self.group,
                {
                    "type": "chat_event",
                    "event_type": "typing",
                    "data": {
                        "user_id": self.scope["user"].id,
                        "is_typing": bool(
                            content.get("is_typing")
                        ),
                    },
                },
            )

            return

        # ---------------------------------------------------------------
        # Message
        # ---------------------------------------------------------------

        message = str(
            content.get(
                "content",
                content.get("message", ""),
            )
        ).strip()

        if not message:
            return

        saved = await self.save_message(message)

        if not saved:
            return

        await self.channel_layer.group_send(
            self.group,
            {
                "type": "chat_event",
                "event_type": "message",
                "data": saved,
            },
        )

    async def chat_event(self, event):

        await self.send_json({
            "type": event.get("event_type"),
            "data": event.get("data"),
        })


# ---------------------------------------------------------------------------
# WebSocket URL patterns
# ---------------------------------------------------------------------------

ws_urlpatterns = [
    re_path(
        r"^ws/notifications/$",
        NotificationConsumer.as_asgi(),
    ),

    re_path(
        r"^ws/chat/(?P<conv_id>\d+)/$",
        ChatConsumer.as_asgi(),
    ),
]


# ---------------------------------------------------------------------------
# ASGI application
# ---------------------------------------------------------------------------

application = ProtocolTypeRouter({
    "http": django_asgi_app,

    "websocket": JWTAuthMiddleware(
        URLRouter(ws_urlpatterns)
    ),
})

# Vercel compatibility
app = application