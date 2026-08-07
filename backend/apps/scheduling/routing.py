from django.urls import re_path
from .consumers import LessonStatusConsumer

websocket_urlpatterns = [
    re_path(r'ws/lessons/(?P<lesson_id>[^/]+)/status/$', LessonStatusConsumer.as_asgi()),
]
